"""OAuth2 provider support: exchanges a provider credential for a verified identity."""
from __future__ import annotations

from dataclasses import dataclass

import httpx

from ..config import get_settings


@dataclass
class OAuthIdentity:
    provider: str
    provider_user_id: str
    email: str
    name: str = ""


class OAuthError(Exception):
    pass


def google_identity(id_token: str) -> OAuthIdentity:
    s = get_settings()
    r = httpx.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token}, timeout=10)
    if r.status_code != 200:
        raise OAuthError("invalid Google token")
    d = r.json()
    if s.google_client_id and d.get("aud") != s.google_client_id:
        raise OAuthError("Google token audience mismatch")
    if d.get("email_verified") not in (True, "true"):
        raise OAuthError("Google email not verified")
    return OAuthIdentity("google", d["sub"], d["email"], d.get("name", ""))


def github_identity(code: str) -> OAuthIdentity:
    s = get_settings()
    with httpx.Client(timeout=10) as c:
        t = c.post(
            "https://github.com/login/oauth/access_token",
            data={"client_id": s.github_client_id, "client_secret": s.github_client_secret, "code": code},
            headers={"Accept": "application/json"},
        ).json()
        token = t.get("access_token")
        if not token:
            raise OAuthError("GitHub code exchange failed")
        h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        user = c.get("https://api.github.com/user", headers=h).json()
        emails = c.get("https://api.github.com/user/emails", headers=h).json()
    primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
    if not primary:
        raise OAuthError("no verified GitHub email")
    return OAuthIdentity("github", str(user["id"]), primary, user.get("name") or "")
