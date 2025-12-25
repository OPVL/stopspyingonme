"""Mock email service for testing."""


class MockEmailService:
    """Mock email service that doesn't send real emails."""

    def __init__(self):
        self.sent_emails = []

    async def send_magic_link(self, to_email: str, token: str) -> bool:
        """Mock sending magic link email."""
        self.sent_emails.append({"to": to_email, "token": token, "type": "magic_link"})
        return True

    def clear_sent_emails(self):
        """Clear sent emails list."""
        self.sent_emails.clear()


# Global mock instance
mock_email_service = MockEmailService()
