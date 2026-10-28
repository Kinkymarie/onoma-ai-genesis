"""Email jobs."""
from ..utils.email import send_email


def send_welcome_email(to: str, name: str) -> bool:
    return send_email(to, "Welcome to Onoma AI", f"Hi {name}, welcome to Onoma AI Genesis!")


def send_password_reset_email(to: str, link: str) -> bool:
    return send_email(to, "Reset your password", f"Use this link to reset your password: {link}")
