"""Email sending (SMTP, or console logging when SMTP is not configured)."""
import smtplib
from email.message import EmailMessage

from ..config.settings import get_settings
from .logger import get_logger

log = get_logger(__name__)
outbox: list[dict] = []


def send_email(to: str, subject: str, body: str) -> bool:
    settings = get_settings()
    outbox.append({"to": to, "subject": subject, "body": body})
    if not settings.smtp_host:
        log.info("email (console)", extra={"to": to, "subject": subject})
        return True
    msg = EmailMessage()
    msg["From"] = settings.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        return True
    except (OSError, smtplib.SMTPException):
        log.exception("email send failed")
        return False
