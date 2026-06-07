from __future__ import annotations

from app.domain.ports.inbound.auth.login_inbound_contracts import (
    LoginCommand,
    LoginUseCase,
    TokenPair,
)
from app.domain.ports.outbound.password_hasher import PasswordHasher
from app.domain.ports.outbound.token_provider import TokenProvider


class LoginUserService(LoginUseCase):
    def __init__(
        self,
        *,
        uow_factory,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        access_token_ttl_seconds: int,
        refresh_token_ttl_seconds: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._access_token_ttl_seconds = access_token_ttl_seconds
        self._refresh_token_ttl_seconds = refresh_token_ttl_seconds

    async def execute(self, command: LoginCommand) -> TokenPair:
        async with self._uow_factory() as uow:
            user = await uow.users.get_user_by_email(email=command.email)
            if not user or not user.password_hash:
                raise ValueError("Invalid credentials")
            if not user.is_active:
                raise ValueError("User account is disabled")

            if not self._password_hasher.verify_password(
                plain_password=command.password, hashed_password=user.password_hash
            ):
                raise ValueError("Invalid credentials")
            if command.org_slug:
                membership = await uow.memberships.get_membership_by_org_slug(
                    org_slug=command.org_slug,
                    user_id=user.id,
                )
            else:
                memberships = await uow.memberships.list_user_memberships(
                    user_id=user.id
                )
                membership = memberships[0] if memberships else None
            if not membership:
                raise ValueError("No organization access")
            claims = {
                "sub": str(user.id),
                "org_id": str(membership.org_id),
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

            await uow.users.update_last_login(user_id=user.id)
            await uow.commit()

            return TokenPair(access_token=access_token, refresh_token=refresh_token)
