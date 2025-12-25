import asyncio
import smtplib
from email.mime.text import MIMEText
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending emails via SMTP relay."""

    def __init__(self) -> None:
        self.smtp_host = settings.relay_host
        self.smtp_port = settings.relay_port
        self.smtp_user = settings.relay_user
        self.smtp_password = settings.relay_password
        self.use_tls = settings.relay_use_tls
        self.from_email = settings.from_email

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader("app/templates/email"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def _send_email_async(
        self, to_email: str, subject: str, content: str
    ) -> bool:
        """Send email asynchronously using thread pool."""
        try:
            # Run SMTP operations in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._send_email_sync, to_email, subject, content
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def _send_email_sync(self, to_email: str, subject: str, content: str) -> None:
        """Synchronous email sending."""
        msg = MIMEText(content, "plain")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    def _render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render email template with context."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    async def send_magic_link(self, to_email: str, token: str) -> bool:
        """Send magic link email using Porter persona template."""
        magic_url = f"{settings.webauthn_origin}/auth/verify?token={token}"

        context = {
            "magic_url": magic_url,
            "email": to_email,
            "expires_minutes": settings.magic_link_ttl // 60,
        }

        subject = "Your secure login link"
        content = self._render_template("magic_link.txt", context)

        return await self._send_email_async(to_email, subject, content)

    async def send_verification_email(
        self, to_email: str, verification_token: str
    ) -> bool:
        """Send email verification using Porter persona template."""
        verification_url = (
            f"{settings.webauthn_origin}/verify-email?token={verification_token}"
        )

        context = {
            "verification_url": verification_url,
            "email": to_email,
        }

        subject = "Verify your email address"
        content = self._render_template("email_verification.txt", context)

        return await self._send_email_async(to_email, subject, content)


# Global email service instance
email_service = EmailService()
