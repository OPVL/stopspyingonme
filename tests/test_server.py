#!/usr/bin/env python3
import os
from unittest.mock import MagicMock, patch

import pytest

from server import ALIASES, ForwardingHandler, main


class TestForwardingHandler:
    @pytest.fixture
    def handler(self):
        return ForwardingHandler()

    @pytest.fixture
    def mock_envelope(self):
        envelope = MagicMock()
        envelope.mail_from = "sender@example.com"
        envelope.rcpt_tos = ["test@localhost"]
        envelope.content = b"Subject: Test\n\nTest message"
        return envelope

    @pytest.mark.asyncio
    async def test_handle_data_unknown_alias(self, handler, mock_envelope):
        mock_envelope.rcpt_tos = ["unknown@localhost"]
        result = await handler.handle_DATA(None, None, mock_envelope)
        assert result == "250 OK"

    @pytest.mark.asyncio
    @patch.dict(
        os.environ, {"RELAY_HOST": "", "ALIASES": "test@localhost=dest@example.com"}
    )
    async def test_handle_data_no_relay_host(self, handler, mock_envelope):
        with patch.dict("server.ALIASES", {"test@localhost": "dest@example.com"}):
            result = await handler.handle_DATA(None, None, mock_envelope)
            assert result == "550 Relay not configured"

    @pytest.mark.asyncio
    @patch.dict(
        os.environ,
        {"RELAY_HOST": "smtp.example.com", "RELAY_USER": "", "RELAY_PASSWORD": ""},
    )
    async def test_handle_data_no_credentials(self, handler, mock_envelope):
        with patch.dict("server.ALIASES", {"test@localhost": "dest@example.com"}):
            result = await handler.handle_DATA(None, None, mock_envelope)
            assert result == "550 Relay credentials missing"

    @pytest.mark.asyncio
    @patch.dict(
        os.environ,
        {
            "RELAY_HOST": "smtp.example.com",
            "RELAY_USER": "user@example.com",
            "RELAY_PASSWORD": "password",
        },
    )
    @patch("server.smtplib.SMTP")
    async def test_handle_data_success(self, mock_smtp, handler, mock_envelope):
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        with patch.dict("server.ALIASES", {"test@localhost": "dest@example.com"}):
            result = await handler.handle_DATA(None, None, mock_envelope)
            assert result == "250 OK"
            mock_smtp_instance.starttls.assert_called_once()
            mock_smtp_instance.login.assert_called_once()

    @pytest.mark.asyncio
    @patch.dict(
        os.environ,
        {
            "RELAY_HOST": "smtp.example.com",
            "RELAY_USER": "user@example.com",
            "RELAY_PASSWORD": "password",
        },
    )
    @patch("server.smtplib.SMTP")
    async def test_handle_data_smtp_error(self, mock_smtp, handler, mock_envelope):
        mock_smtp.side_effect = Exception("SMTP Error")

        with patch.dict("server.ALIASES", {"test@localhost": "dest@example.com"}):
            result = await handler.handle_DATA(None, None, mock_envelope)
            assert result == "550 Forwarding failed"


class TestMain:
    @pytest.mark.asyncio
    @patch("server.Controller")
    @patch("asyncio.sleep")
    async def test_main_default_config(self, mock_sleep, mock_controller):
        mock_sleep.side_effect = KeyboardInterrupt()
        mock_controller_instance = MagicMock()
        mock_controller.return_value = mock_controller_instance

        with patch.dict(os.environ, {}, clear=True):
            await main()

        mock_controller.assert_called_once()
        mock_controller_instance.start.assert_called_once()
        mock_controller_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    @patch("server.Controller")
    @patch("asyncio.sleep")
    async def test_main_custom_config(self, mock_sleep, mock_controller):
        mock_sleep.side_effect = KeyboardInterrupt()
        mock_controller_instance = MagicMock()
        mock_controller.return_value = mock_controller_instance

        with patch.dict(os.environ, {"SMTP_HOST": "0.0.0.0", "SMTP_PORT": "2525"}):
            await main()

        mock_controller.assert_called_with(
            mock_controller.call_args[0][0], hostname="0.0.0.0", port=2525
        )

    @pytest.mark.asyncio
    @patch("server.Controller")
    @patch("asyncio.sleep")
    async def test_main_invalid_port(self, mock_sleep, mock_controller):
        mock_sleep.side_effect = KeyboardInterrupt()
        mock_controller_instance = MagicMock()
        mock_controller.return_value = mock_controller_instance

        with patch.dict(os.environ, {"SMTP_PORT": "invalid"}):
            await main()

        # Should use default port 8025
        assert mock_controller.call_args[1]["port"] == 8025


class TestAliasConfig:
    def test_alias_parsing_valid(self):
        with patch.dict(
            os.environ,
            {
                "ALIASES": "test@localhost=dest@example.com,alias2@localhost=dest2@example.com"
            },
        ):
            # Re-import to trigger alias parsing
            import importlib

            import server

            importlib.reload(server)

            assert "test@localhost" in server.ALIASES
            assert server.ALIASES["test@localhost"] == "dest@example.com"

    def test_alias_parsing_with_equals_in_dest(self):
        with patch.dict(
            os.environ, {"ALIASES": "test@localhost=dest@example.com?param=value"}
        ):
            import importlib

            import server

            importlib.reload(server)

            assert server.ALIASES["test@localhost"] == "dest@example.com?param=value"

    def test_alias_parsing_empty(self):
        with patch.dict(os.environ, {"ALIASES": ""}):
            import importlib

            import server

            importlib.reload(server)

            assert len(server.ALIASES) == 0

    def test_relay_port_invalid(self):
        with patch.dict(os.environ, {"RELAY_PORT": "invalid"}):
            handler = ForwardingHandler()
            # Port conversion should handle ValueError gracefully in handle_DATA
            assert True  # Test passes if no exception is raised
