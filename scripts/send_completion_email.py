"""Send or draft the completion notification using environment-only SMTP configuration."""

from __future__ import annotations

import argparse
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    recipient = os.getenv("MORPHOLOGY_NOTIFY_EMAIL")
    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    message = EmailMessage()
    message["Subject"] = "[Morphology Studio] 开源整理与公开发布状态报告"
    message["To"] = recipient or "undisclosed-recipient"
    message["From"] = username or "morphology-studio@localhost"
    message.set_content(args.body.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "completion_email.eml").write_bytes(message.as_bytes())
    (args.output / "completion_email.md").write_text(message.get_content(), encoding="utf-8")
    if not recipient:
        print("EMAIL_NOT_SENT_MISSING_RECIPIENT")
        return 2
    if not host or not username or not password:
        print("EMAIL_NOT_SENT_NO_TRANSPORT")
        return 3
    port = int(os.getenv("SMTP_PORT", "587"))
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
    with smtplib.SMTP(host, port, timeout=30) as client:
        if use_tls:
            client.starttls()
        client.login(username, password)
        client.send_message(message)
    print("EMAIL_SENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
