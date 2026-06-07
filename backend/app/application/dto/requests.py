from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StrictInt, StrictStr


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    email: EmailStr
    password: StrictStr = Field(..., min_length=8, max_length=128)
    full_name: StrictStr = Field(..., min_length=2, max_length=255)
    organization_name: StrictStr = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    email: EmailStr
    password: StrictStr = Field(..., min_length=8, max_length=128)
    org_slug: StrictStr | None = None


class SwitchOrgRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    target_org_id: StrictStr


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    refresh_token: StrictStr


class InviteMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    email: EmailStr
    role: StrictStr = Field(..., pattern="^(OWNER|ADMIN|MEMBER)$")


class AcceptInvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    invitation_token: StrictStr


class RegisterViaInvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    invitation_token: StrictStr
    password: StrictStr = Field(..., min_length=8, max_length=128)
    full_name: StrictStr = Field(..., min_length=2, max_length=255)


class MembersListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    page: StrictInt = Field(default=1, ge=1)
    page_size: StrictInt = Field(default=20, ge=1, le=100)


class PatchMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    role: StrictStr | None = Field(default=None, pattern="^(OWNER|ADMIN|MEMBER)$")
    status: StrictStr | None = Field(
        default=None, pattern="^(ACTIVE|SUSPENDED|INVITED)$"
    )


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    message: StrictStr = Field(..., min_length=1, max_length=10000)


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    query: StrictStr = Field(..., min_length=1, max_length=10000)
    top_k: StrictInt = Field(default=5, ge=1, le=50)
