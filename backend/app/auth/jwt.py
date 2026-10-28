from __future__ import annotations

import hashlib
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from ..config import get_settings

_blacklist: dict[str, float] = {}
_redis = None


def _get_redis():
    global _redis
    url = get_settings().redis_url
    if url and _redis is None:
        import redis

        _redis = redis.Redis.from_url(url)
    return _redis


def create_token(subject: str, token_type: str, expires: timedelta, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "type": token_type, "iat": now, "exp": now + expires, "jti": uuid.uuid4().hex}
    payload.update(extra or {})
    s = get_settings()
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def create_access_token(user_id: int) -> str:
    return create_token(str(user_id), "access", timedelta(minutes=get_settings().access_token_minutes))


def create_refresh_token(user_id: int) -> str:
    return create_token(str(user_id), "refresh", timedelta(days=get_settings().refresh_token_days))


def decode_token(token: str, expected_type: str = "access") -> dict:
    s = get_settings()
    payload = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("wrong token type")
    if is_blacklisted(payload["jti"]):
        raise jwt.InvalidTokenError("token revoked")
    return payload


def blacklist(jti: str, exp: float) -> None:
    ttl = max(int(exp - time.time()), 1)
    r = _get_redis()
    if r is not None:
        r.setex(f"bl:{jti}", ttl, 1)
    else:
        _blacklist[jti] = exp


def is_blacklisted(jti: str) -> bool:
    r = _get_redis()
    if r is not None:
        return bool(r.exists(f"bl:{jti}"))
    exp = _blacklist.get(jti)
    if exp is not None and exp < time.time():
        _blacklist.pop(jti, None)
        return False
    return exp is not None


def random_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
