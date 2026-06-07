from __future__ import annotations

import html as html_module
import logging
import smtplib
import subprocess
import tempfile
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.domain.ports.outbound.email_sender import EmailSender

logger = logging.getLogger(__name__)


class NullEmailSender(EmailSender):

    def send_invitation_email(
        self,
        *,
        to_email: str,
        invite_url: str,
        org_name: str,
        role: str,
        expires_in_hours: int,
    ) -> None:
        return None


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        from_email: str,
        from_name: str,
        templates_dir: str | Path | None = None,
        mjml_binary_path: str = "mjml",
    ) -> None:
        self._host = host
        self._port = port
        self._username = (username or "").strip() or None
        self._password = password or ""
        self._use_tls = use_tls
        self._from_email = from_email
        self._from_name = from_name.strip() or from_email
        self._mjml_binary_path = mjml_binary_path
        tpl_dir = (
            Path(templates_dir)
            if templates_dir is not None
            else Path(__file__).resolve().parent
        )
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(tpl_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def send_invitation_email(
        self,
        *,
        to_email: str,
        invite_url: str,
        org_name: str,
        role: str,
        expires_in_hours: int,
    ) -> None:
        mjml_source = self._jinja_env.get_template("invitation_email.mjml").render(
            invite_url=invite_url,
            org_name=org_name,
            role=role,
            expires_in_hours=expires_in_hours,
        )
        try:
            html_body = self._compile_mjml(mjml_source)
            logger.info("Compiled MJML invitation template successfully")
        except (RuntimeError, OSError, FileNotFoundError) as exc:
            logger.warning(
                "MJML CLI unavailable or failed (%s); "
                "sending invitation with simple HTML instead.",
                exc,
            )
            html_body = self._simple_invitation_html(
                invite_url=invite_url,
                org_name=org_name,
                role=role,
                expires_in_hours=expires_in_hours,
            )

        msg = EmailMessage()
        msg["Subject"] = f"You're invited to join {org_name} on MindVault"
        msg["From"] = f"{self._from_name} <{self._from_email}>"
        msg["To"] = to_email
        msg.set_content(
            (
                f"You've been invited to join {org_name} on MindVault as {role}.\n\n"
                f"Accept here:\n{invite_url}\n"
            )
        )
        msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
            if self._use_tls:
                smtp.starttls()
            if self._username and self._password:
                smtp.login(self._username, self._password)
            smtp.send_message(msg)

    def _compile_mjml(self, mjml_source: str) -> str:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".mjml", encoding="utf-8", delete=True
        ) as tmp:
            tmp.write(mjml_source)
            tmp.flush()
            process = subprocess.run(
                [self._mjml_binary_path, tmp.name, "-s"],
                text=True,
                capture_output=True,
                timeout=120,
                check=False,
            )
        if process.returncode != 0:
            stderr = (process.stderr or "").strip()
            raise RuntimeError(f"Failed to compile MJML: {stderr}")
        stdout = process.stdout or ""
        if not stdout.strip():
            raise RuntimeError(
                "MJML compiler produced empty output; is `mjml` installed and on PATH?"
            )
        return stdout

    @staticmethod
    def _simple_invitation_html(
        *,
        invite_url: str,
        org_name: str,
        role: str,
        expires_in_hours: int,
    ) -> str:
        safe_org = html_module.escape(org_name)
        safe_role = html_module.escape(role)
        safe_url = html_module.escape(invite_url, quote=True)
        exp_block = ""
        if expires_in_hours:
            exp_block = (
                "<p>This invitation expires in <strong>"
                f"{int(expires_in_hours)}"
                "</strong> hours.</p>"
            )
        return (
            "<!DOCTYPE html>"
            '<html><body style="font-family:system-ui,sans-serif;line-height:1.5;">'
            f"<p>You've been invited to join <strong>{safe_org}</strong> on MindVault "
            f"as <strong>{safe_role}</strong>.</p>"
            f"{exp_block}"
            f'<p><a href="{safe_url}">Accept invitation</a></p>'
            f'<p style="font-size:0.9em;color:#555;">If the button does not work, '
            f"copy this link:<br>{safe_url}</p>"
            "</body></html>"
        )
