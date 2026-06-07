from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.application.dto.requests import (
    AcceptInvitationRequest,
    InviteMemberRequest,
    LoginRequest,
    PatchMemberRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterViaInvitationRequest,
    SwitchOrgRequest,
)
from app.application.dto.responses import (
    InviteMemberResponse,
    MFAPartialResponse,
    MeResponse,
    MembersListResponse,
    OrganizationsListResponse,
    RegisterResponse,
    SwitchOrgResponse,
    TokenPairResponse,
)
from app.domain.ports.inbound.auth.org_switch_inbound_contracts import (
    SwitchOrganizationCommand,
)
from app.domain.ports.inbound.auth.registration_inbound_contracts import (
    RegisterUserCommand,
)
from app.application.tasks.audit_tasks import record_audit_event
from app.application.tasks.email_tasks import send_organization_invitation_email
from app.infrastructure.config import settings
from app.infrastructure.di.container import Container
from app.infrastructure.security.auth import get_current_claims
from app.infrastructure.security.permissions import requires_role

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse)
async def register(
    payload: RegisterRequest,
    service=Depends(Container.get_register_user_service),
) -> RegisterResponse:
    try:
        result = await service.execute(
            RegisterUserCommand(
                email=str(payload.email),
                password=payload.password,
                full_name=payload.full_name,
                organization_name=payload.organization_name,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    return RegisterResponse(
        user_id=str(result.user_id),
        default_org_id=str(result.default_org_id) if result.default_org_id else None,
    )

@router.post("/login", response_model=TokenPairResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    iam_service=Depends(Container.get_iam_service),
) -> TokenPairResponse | MFAPartialResponse:
    try:
        result = await iam_service.login(
            email=str(payload.email),
            password=payload.password,
            org_slug=payload.org_slug,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    if result.get("mfa_required"):
        return MFAPartialResponse(
            mfa_attempt_token=result["mfa_attempt_token"],
            expires_in_seconds=result["expires_in_seconds"],
        )
    return TokenPairResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result.get("token_type", "bearer"),
    )

@router.post("/switch-org", response_model=SwitchOrgResponse)
async def switch_org(
    payload: SwitchOrgRequest,
    claims: dict = Depends(get_current_claims),
    service=Depends(Container.get_switch_org_service),
) -> SwitchOrgResponse:
    try:
        target_org_id = UUID(payload.target_org_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid target_org_id UUID",
        ) from exc

    try:
        result = await service.execute(
            SwitchOrganizationCommand(
                user_id=UUID(str(claims["sub"])),
                target_org_id=target_org_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    return SwitchOrgResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        active_org_id=str(result.active_org_id),
    )

@router.get("/me", response_model=MeResponse)
async def me(claims: dict = Depends(get_current_claims)) -> MeResponse:
    return MeResponse(
        user_id=str(claims.get("sub")),
        org_id=str(claims.get("org_id")),
        role=str(claims.get("role", "member")),
    )

@router.get("/me/orgs", response_model=OrganizationsListResponse)
async def list_my_organizations_me(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    claims: dict = Depends(get_current_claims),
    iam_service=Depends(Container.get_iam_service),
) -> OrganizationsListResponse:
    result = await iam_service.list_my_organizations(
        actor_claims=claims, page=page, page_size=page_size
    )
    return OrganizationsListResponse(**result)

@router.post("/refresh", response_model=TokenPairResponse)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    iam_service=Depends(Container.get_iam_service),
) -> TokenPairResponse:
    try:
        result = await iam_service.refresh(refresh_token=payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    return TokenPairResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    claims: dict = Depends(get_current_claims),
    iam_service=Depends(Container.get_iam_service),
) -> None:
    await iam_service.logout(access_claims=claims)

@router.post("/orgs/{org_id}/invite", response_model=InviteMemberResponse)
async def invite_member(
    org_id: UUID,
    payload: InviteMemberRequest,
    claims: dict = Depends(requires_role("OWNER", "ADMIN")),
    iam_service=Depends(Container.get_iam_service),
) -> InviteMemberResponse:
    try:
        invited = await iam_service.create_invitation(
            actor_claims=claims,
            org_id=org_id,
            email=str(payload.email),
            role=payload.role,
            ttl_seconds=settings.invitation_ttl_seconds,
        )
    except ValueError as exc:
        msg = str(exc)
        if msg == "Organization not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from exc
        if msg.startswith("User is already"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=msg
            ) from exc
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg) from exc

    send_organization_invitation_email.delay(
        to_email=invited["to_email"],
        invite_url=invited["invite_url"],
        org_name=invited["organization_name"],
        role=invited["display_role"],
        expires_in_hours=invited["expires_in_hours"],
    )
    record_audit_event.delay(
        event_type="USER_INVITED",
        actor_id=str(claims["sub"]),
        org_id=str(org_id),
        ip_address=None,
        user_agent=None,
        metadata={"email": str(payload.email), "role": payload.role},
    )
    return InviteMemberResponse(
        invitation_token=invited["invitation_token"],
        invite_url=invited["invite_url"],
    )

@router.post("/invitations/register", response_model=RegisterResponse)
async def register_via_invitation(
    payload: RegisterViaInvitationRequest,
    iam_service=Depends(Container.get_iam_service),
) -> RegisterResponse:
    try:
        result = await iam_service.register_via_invitation(
            token=payload.invitation_token,
            password=payload.password,
            full_name=payload.full_name,
        )
    except ValueError as exc:
        detail = str(exc)
        if "already exists" in detail:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=detail
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc
    return RegisterResponse(
        user_id=result["user_id"],
        default_org_id=result["default_org_id"],
    )

@router.post("/invitations/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_invitation(
    payload: AcceptInvitationRequest,
    claims: dict = Depends(get_current_claims),
    iam_service=Depends(Container.get_iam_service),
) -> None:
    try:
        await iam_service.accept_invitation(
            token=payload.invitation_token, user_id=UUID(str(claims["sub"]))
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

@router.get("/orgs/{org_id}/members", response_model=MembersListResponse)
async def list_members(
    org_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    claims: dict = Depends(requires_role("OWNER", "ADMIN")),
    iam_service=Depends(Container.get_iam_service),
) -> MembersListResponse:
    try:
        result = await iam_service.list_org_members(
            actor_claims=claims, org_id=org_id, page=page, page_size=page_size
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    return MembersListResponse(**result)

@router.get("/orgs", response_model=OrganizationsListResponse)
async def list_my_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    claims: dict = Depends(get_current_claims),
    iam_service=Depends(Container.get_iam_service),
) -> OrganizationsListResponse:
    result = await iam_service.list_my_organizations(
        actor_claims=claims, page=page, page_size=page_size
    )
    return OrganizationsListResponse(**result)

@router.patch("/orgs/{org_id}/members/{user_id}")
async def patch_member(
    org_id: UUID,
    user_id: UUID,
    payload: PatchMemberRequest,
    claims: dict = Depends(requires_role("OWNER", "ADMIN")),
    iam_service=Depends(Container.get_iam_service),
) -> dict:
    try:
        return await iam_service.patch_member(
            actor_claims=claims,
            org_id=org_id,
            user_id=user_id,
            role=payload.role,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

@router.delete(
    "/orgs/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_member(
    org_id: UUID,
    user_id: UUID,
    claims: dict = Depends(requires_role("OWNER", "ADMIN")),
    iam_service=Depends(Container.get_iam_service),
) -> None:
    try:
        await iam_service.delete_member(
            actor_claims=claims, org_id=org_id, user_id=user_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
