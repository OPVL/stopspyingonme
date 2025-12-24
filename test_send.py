#!/usr/bin/env python3

# pragma: no cover

import smtplib
import sys
from email.message import EmailMessage


def send_test_email(to_alias, subject="Test Email", body="This is a test email."):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = "sender@example.com"
    msg["To"] = to_alias

    try:
        with smtplib.SMTP("localhost", 8025) as smtp:
            smtp.send_message(msg)
        print(f"✓ Email sent to {to_alias}")
    except Exception as e:
        print(f"✗ Failed to send: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        to_alias = sys.argv[1]
    else:
        to_alias = "test@localhost"

    send_test_email(to_alias)
