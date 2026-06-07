from __future__ import annotations

from app.domain.ports.inbound.auth.org_switch_inbound_contracts import (
    SwitchOrganizationCommand,
    SwitchOrganizationResult,
    SwitchOrganizationUseCase,
)
from app.domain.ports.outbound.token_provider import TokenProvider


class SwitchOrganizationService(SwitchOrganizationUseCase):
    def __init__(
        self,
        *,
        uow_factory,
        token_provider: TokenProvider,
        access_token_ttl_seconds: int,
        refresh_token_ttl_seconds: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._token_provider = token_provider
        self._access_token_ttl_seconds = access_token_ttl_seconds
        self._refresh_token_ttl_seconds = refresh_token_ttl_seconds

    async def execute(
        self, command: SwitchOrganizationCommand
    ) -> SwitchOrganizationResult:
        async with self._uow_factory() as uow:
            membership = await uow.memberships.get_active_membership(
                user_id=command.user_id,
                org_id=command.target_org_id,
            )
            if not membership:
                raise ValueError("User does not have access to target organization")

            claims = {
                "sub": str(command.user_id),
                "org_id": str(command.target_org_id),
                "role": str(membership.role),
            }
            access_token = self._token_provider.issue_access_token(
                claims=claims,
                expires_in_seconds=self._access_token_ttl_seconds,
            )
            refresh_token = self._token_provider.issue_refresh_token(
                claims=claims,
                expires_in_seconds=self._refresh_token_ttl_seconds,
            )
            return SwitchOrganizationResult(
                access_token=access_token,
                refresh_token=refresh_token,
                active_org_id=command.target_org_id,
            )
