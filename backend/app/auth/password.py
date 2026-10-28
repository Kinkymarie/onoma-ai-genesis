"""Bcrypt password hashing."""
import bcrypt

from ..config.security import get_security_settings


def hash_password(password: str) -> str:
    rounds = get_security_settings().bcrypt_rounds
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt(rounds)).decode()


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False
