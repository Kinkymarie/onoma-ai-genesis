"""JWT access/refresh tokens with blacklist and refresh rotation."""
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from ..config.security import get_security_settings
from ..utils.constants import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from ..utils.exceptions import Unauthorized


class TokenBlacklist:
    """In-memory blacklist of revoked token ids (jti) until their expiry."""

    def __init__(self) -> None:
        self._revoked: dict[str, float] = {}
        self._lock = threading.Lock()

    def revoke(self, jti: str, exp: float) -> None:
        with self._lock:
            self._revoked[jti] = exp
            now = time.time()
            for k in [k for k, v in self._revoked.items() if v < now]:
                del self._revoked[k]

    def is_revoked(self, jti: str) -> bool:
        return jti in self._revoked

    def clear(self) -> None:
        self._revoked.clear()


blacklist = TokenBlacklist()


def _encode(subject: str, token_type: str, expires: timedelta, extra: dict | None = None) -> str:
    s = get_security_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject, "type": token_type, "jti": uuid.uuid4().hex,
        "iat": now, "exp": now + expires, **(extra or {}),
    }
    return jwt.encode(payload, s.jwt_secret_key, algorithm=s.jwt_algorithm)


def create_access_token(user_id: str, role: str = "member") -> str:
    s = get_security_settings()
    return _encode(user_id, TOKEN_TYPE_ACCESS, timedelta(minutes=s.access_token_minutes), {"role": role})


def create_refresh_token(user_id: str) -> str:
    s = get_security_settings()
    return _encode(user_id, TOKEN_TYPE_REFRESH, timedelta(days=s.refresh_token_days))


def decode_token(token: str, expected_type: str = TOKEN_TYPE_ACCESS) -> dict:
    s = get_security_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret_key, algorithms=[s.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token expired")
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token")
    if payload.get("type") != expected_type:
        raise Unauthorized("Wrong token type")
    if blacklist.is_revoked(payload.get("jti", "")):
        raise Unauthorized("Token revoked")
    return payload


def revoke_token(token: str) -> None:
    s = get_security_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret_key, algorithms=[s.jwt_algorithm],
                             options={"verify_exp": False})
    except jwt.InvalidTokenError:
        return
    blacklist.revoke(payload["jti"], float(payload["exp"]))


def refresh_tokens(refresh_token: str, role_lookup) -> tuple[str, str]:
    """Rotate a refresh token: revoke the old one and issue a new pair."""
    payload = decode_token(refresh_token, TOKEN_TYPE_REFRESH)
    role = role_lookup(payload["sub"])
    if role is None:
        raise Unauthorized("User no longer exists")
    blacklist.revoke(payload["jti"], float(payload["exp"]))
    return create_access_token(payload["sub"], role), create_refresh_token(payload["sub"])
