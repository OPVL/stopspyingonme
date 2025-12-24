#!/usr/bin/env python3
import asyncio
import os
import smtplib
from email.message import EmailMessage

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer
from dotenv import load_dotenv

load_dotenv()

# Parse aliases from env
ALIASES = {}
for alias_pair in os.getenv("ALIASES", "").split(","):
    if "=" in alias_pair:
        alias, dest = alias_pair.strip().split("=")
        ALIASES[alias.strip()] = dest.strip()


class ForwardingHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"\n[RECEIVED] From: {envelope.mail_from}")
        print(f"[RECEIVED] To: {envelope.rcpt_tos}")

        for rcpt in envelope.rcpt_tos:
            if rcpt not in ALIASES:
                print(f"[REJECTED] Unknown alias: {rcpt}")
                continue

            destination = ALIASES[rcpt]
            print(f"[FORWARDING] {rcpt} -> {destination}")

            try:
                # Create forwarded message
                msg = EmailMessage()
                msg.set_content(envelope.content.decode("utf-8", errors="replace"))
                msg["From"] = envelope.mail_from
                msg["To"] = destination
                msg["Subject"] = f"[Forwarded via {rcpt}]"

                # Forward via SMTP relay
                relay_host = os.getenv("RELAY_HOST")
                relay_port = int(os.getenv("RELAY_PORT", 587))
                relay_user = os.getenv("RELAY_USER")
                relay_pass = os.getenv("RELAY_PASSWORD")

                assert relay_host is str
                assert relay_user is str
                assert relay_pass is str

                with smtplib.SMTP(relay_host, relay_port) as smtp:
                    smtp.starttls()
                    smtp.login(relay_user, relay_pass)
                    smtp.send_message(msg)

                print(f"[SUCCESS] Forwarded to {destination}")
            except Exception as e:
                print(f"[ERROR] Failed to forward: {e}")
                return "550 Forwarding failed"

        return "250 OK"


async def main():
    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", 8025))

    print(f"\n{'='*60}")
    print(f"Email Privacy Service - Minimal Prototype")
    print(f"{'='*60}")
    print(f"SMTP Server: {host}:{port}")
    print(f"Configured aliases:")
    for alias, dest in ALIASES.items():
        print(f"  {alias} -> {dest}")
    print(f"{'='*60}\n")

    controller = Controller(ForwardingHandler(), hostname=host, port=port)
    controller.start()

    print(f"[RUNNING] Server started. Press Ctrl+C to stop.\n")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOPPED] Shutting down...")
        controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
