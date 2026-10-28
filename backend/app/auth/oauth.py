"""OAuth2 providers (Google, GitHub) using the authorization-code flow."""
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from ..config.security import get_security_settings
from ..utils.exceptions import BadRequest, ProviderError


@dataclass(frozen=True)
class OAuthProvider:
    name: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scope: str

    def credentials(self) -> tuple[str, str]:
        s = get_security_settings()
        return getattr(s, f"{self.name}_client_id"), getattr(s, f"{self.name}_client_secret")

    def redirect_uri(self) -> str:
        return f"{get_security_settings().oauth_redirect_base}/{self.name}/callback"

    def authorization_url(self, state: str | None = None) -> tuple[str, str]:
        client_id, _ = self.credentials()
        if not client_id:
            raise BadRequest(f"{self.name} OAuth is not configured")
        state = state or secrets.token_urlsafe(16)
        query = urlencode({
            "client_id": client_id, "redirect_uri": self.redirect_uri(),
            "response_type": "code", "scope": self.scope, "state": state,
        })
        return f"{self.authorize_url}?{query}", state

    def fetch_profile(self, code: str) -> dict:
        """Exchange the code and return {email, name}."""
        client_id, client_secret = self.credentials()
        if not client_id:
            raise BadRequest(f"{self.name} OAuth is not configured")
        try:
            with httpx.Client(timeout=10) as client:
                tok = client.post(self.token_url, headers={"Accept": "application/json"}, data={
                    "client_id": client_id, "client_secret": client_secret, "code": code,
                    "redirect_uri": self.redirect_uri(), "grant_type": "authorization_code",
                })
                tok.raise_for_status()
                access = tok.json().get("access_token")
                if not access:
                    raise BadRequest("OAuth token exchange failed")
                auth_header = " ".join(["Bearer", access])
                info = client.get(self.userinfo_url, headers={"Authorization": auth_header})
                info.raise_for_status()
                data = info.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"{self.name} OAuth request failed") from exc
        email = data.get("email")
        if not email:
            raise BadRequest("OAuth provider did not return an email")
        return {"email": email, "name": data.get("name") or data.get("login") or email.split("@")[0]}


PROVIDERS: dict[str, OAuthProvider] = {
    "google": OAuthProvider(
        "google", "https://accounts.google.com/o/oauth2/v2/auth", "https://oauth2.googleapis.com/token",
        "https://openidconnect.googleapis.com/v1/userinfo", "openid email profile"),
    "github": OAuthProvider(
        "github", "https://github.com/login/oauth/authorize", "https://github.com/login/oauth/access_token",
        "https://api.github.com/user", "read:user user:email"),
}


def get_provider(name: str) -> OAuthProvider:
    provider = PROVIDERS.get(name)
    if provider is None:
        raise BadRequest(f"Unknown OAuth provider: {name}")
    return provider
