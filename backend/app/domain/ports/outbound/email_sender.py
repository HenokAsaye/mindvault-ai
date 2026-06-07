from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send_invitation_email(
        self,
        *,
        to_email: str,
        invite_url: str,
        org_name: str,
        role: str,
        expires_in_hours: int,
    ) -> None: ...
