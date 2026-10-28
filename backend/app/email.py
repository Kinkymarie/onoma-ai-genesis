from __future__ import annotations

import logging

import httpx

from .config import get_settings

log = logging.getLogger("onoma.email")


def send_email(to: str, subject: str, body: str) -> None:
    key = get_settings().sendgrid_api_key
    if not key:
        log.info("email (not sent, no provider configured) to=%s subject=%s", to, subject)
        return
    httpx.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": "no-reply@onoma.ai"},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        },
        timeout=10,
    )
