#!/usr/bin/env python3
import asyncio
import os
import smtplib
from email.message import EmailMessage

from aiosmtpd.controller import Controller
from dotenv import load_dotenv

load_dotenv()

# Parse aliases from env
ALIASES = {}
for alias_pair in os.getenv("ALIASES", "").split(","):
    if "=" in alias_pair:
        try:
            alias, dest = alias_pair.strip().split("=", 1)
            ALIASES[alias.strip()] = dest.strip()
        except ValueError:
            print(f"[WARNING] Invalid alias format: {alias_pair}")


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
                if not relay_host:
                    print("[ERROR] RELAY_HOST not configured")
                    return "550 Relay not configured"

                try:
                    relay_port = int(os.getenv("RELAY_PORT", 587))
                except ValueError:
                    relay_port = 587

                relay_user = os.getenv("RELAY_USER")
                relay_pass = os.getenv("RELAY_PASSWORD")

                if not relay_user or not relay_pass:
                    print("[ERROR] RELAY credentials not configured")
                    return "550 Relay credentials missing"

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
    try:
        port = int(os.getenv("SMTP_PORT", 8025))
    except ValueError:
        port = 8025
        print(f"[WARNING] Invalid SMTP_PORT, using default: {port}")

    print(f"\n{'='*60}")
    print("Email Privacy Service - Minimal Prototype")
    print(f"{'='*60}")
    print(f"SMTP Server: {host}:{port}")
    print("Configured aliases:")
    if ALIASES:
        for alias, dest in ALIASES.items():
            print(f"  {alias} -> {dest}")
    else:
        print("  [WARNING] No aliases configured")
    print(f"{'='*60}\n")

    controller = Controller(ForwardingHandler(), hostname=host, port=port)
    controller.start()

    print("[RUNNING] Server started. Press Ctrl+C to stop.\n")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOPPED] Shutting down...")
        controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
