from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.email import EmailService


class TestEmailService:
    """Test email service functionality."""

    @pytest.fixture
    def email_service(self) -> EmailService:
        """Create email service instance."""
        return EmailService()

    @pytest.fixture
    def mock_smtp(self):
        """Mock SMTP server."""
        with patch("app.services.email.smtplib.SMTP") as mock:
            smtp_instance = MagicMock()
            mock.return_value.__enter__.return_value = smtp_instance
            yield smtp_instance

    async def test_send_magic_link_success(
        self, email_service: EmailService, mock_smtp: MagicMock
    ) -> None:
        """Test successful magic link email sending."""
        result = await email_service.send_magic_link("test@example.com", "test_token")

        assert result is True
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once()
        mock_smtp.send_message.assert_called_once()

    async def test_send_magic_link_smtp_failure(
        self, email_service: EmailService, mock_smtp: MagicMock
    ) -> None:
        """Test magic link email sending with SMTP failure."""
        mock_smtp.send_message.side_effect = Exception("SMTP Error")

        result = await email_service.send_magic_link("test@example.com", "test_token")

        assert result is False

    async def test_send_verification_email_success(
        self, email_service: EmailService, mock_smtp: MagicMock
    ) -> None:
        """Test successful verification email sending."""
        result = await email_service.send_verification_email(
            "test@example.com", "verification_token"
        )

        assert result is True
        mock_smtp.send_message.assert_called_once()

    def test_render_template_magic_link(self, email_service: EmailService) -> None:
        """Test magic link template rendering."""
        context = {
            "magic_url": "https://example.com/verify?token=test",
            "email": "test@example.com",
            "expires_minutes": 15,
        }

        content = email_service._render_template("magic_link.txt", context)

        assert "quitspyingonme" in content
        assert "Porter" in content
        assert "sign-in link" in content
        assert str(context["magic_url"]) in content
        assert str(context["expires_minutes"]) in content

    def test_render_template_verification(self, email_service: EmailService) -> None:
        """Test verification email template rendering."""
        context = {
            "verification_url": "https://example.com/verify-email?token=test",
            "email": "test@example.com",
        }

        content = email_service._render_template("email_verification.txt", context)

        assert "quitspyingonme" in content
        assert "Porter" in content
        assert "Verify your email address" in content
        assert context["verification_url"] in content
        assert context["email"] in content

    async def test_send_email_async_thread_execution(
        self, email_service: EmailService
    ) -> None:
        """Test that email sending uses thread pool."""
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop_instance = AsyncMock()
            mock_loop.return_value = mock_loop_instance

            await email_service._send_email_async(
                "test@example.com", "Test Subject", "Test Content"
            )

            mock_loop_instance.run_in_executor.assert_called_once()

    def test_send_email_sync_message_construction(
        self, email_service: EmailService, mock_smtp: MagicMock
    ) -> None:
        """Test synchronous email sending constructs message correctly."""
        email_service._send_email_sync(
            "test@example.com", "Test Subject", "Test Content"
        )

        # Verify SMTP operations
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with(
            email_service.smtp_user, email_service.smtp_password
        )
        mock_smtp.send_message.assert_called_once()

        # Check message construction
        call_args = mock_smtp.send_message.call_args[0][0]
        assert call_args["Subject"] == "Test Subject"
        assert call_args["To"] == "test@example.com"
        assert call_args["From"] == email_service.from_email
