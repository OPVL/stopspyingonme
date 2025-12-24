import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

    async def send_magic_link(self, to_email: str, token: str) -> bool:
        """Send magic link email."""
        try:
            # Create magic link URL
            magic_url = f"{settings.webauthn_origin}/auth/verify?token={token}"

            # Create email content
            subject = "Your Magic Link - Stop Spying On Me"

            html_content = f"""
            <html>
            <body>
                <h2>Your Magic Link</h2>
                <p>Click the link below to sign in to your Stop Spying On Me
                account:</p>
                <p><a href="{magic_url}" style="background-color: #007bff;
                color: white; padding: 10px 20px; text-decoration: none;
                border-radius: 5px;">Sign In</a></p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{magic_url}</p>
                <p>This link will expire in 15 minutes.</p>
                <p>If you didn't request this link, you can safely ignore this
                email.</p>
                <hr>
                <p><small>Stop Spying On Me - Email Privacy Service</small></p>
            </body>
            </html>
            """

            text_content = f"""
            Your Magic Link - Stop Spying On Me

            Click the link below to sign in to your account:
            {magic_url}

            This link will expire in 15 minutes.

            If you didn't request this link, you can safely ignore this email.

            Stop Spying On Me - Email Privacy Service
            """

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Add text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            # Log error in production
            print(f"Failed to send magic link email: {e}")
            return False


# Global email service instance
email_service = EmailService()
