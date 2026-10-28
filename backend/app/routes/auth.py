"""Authentication endpoints."""
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..auth import jwt as jwt_tokens
from ..auth import oauth
from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import (
    LoginRequest, PasswordChange, RefreshRequest, TokenPair, TotpCode, User, UserCreate, UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, c: Container = Depends(get_container)):
    user = c.users.register(data)
    c.audit.record(user.id, "user.register", f"user:{user.id}")
    return user


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, c: Container = Depends(get_container)):
    user = c.users.authenticate(data.email, data.password, data.totp_code)
    c.audit.record(user.id, "user.login", f"user:{user.id}")
    return c.users.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, c: Container = Depends(get_container)):
    return c.users.refresh(data.refresh_token)


@router.post("/logout")
def logout(body: RefreshRequest | None = None, user: User = Depends(get_current_user),
           creds: HTTPAuthorizationCredentials = Depends(_bearer), c: Container = Depends(get_container)):
    jwt_tokens.revoke_token(creds.credentials)
    if body:
        jwt_tokens.revoke_token(body.refresh_token)
    c.audit.record(user.id, "user.logout", f"user:{user.id}")
    return {"success": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/password")
def change_password(data: PasswordChange, user: User = Depends(get_current_user),
                    c: Container = Depends(get_container)):
    c.users.change_password(user.id, data.current_password, data.new_password)
    c.audit.record(user.id, "user.password_change", f"user:{user.id}")
    return {"success": True}


@router.post("/2fa/setup")
def totp_setup(user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return {"provisioning_uri": c.users.begin_totp(user.id)}


@router.post("/2fa/confirm", response_model=UserOut)
def totp_confirm(data: TotpCode, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.users.confirm_totp(user.id, data.code)


@router.post("/2fa/disable", response_model=UserOut)
def totp_disable(data: TotpCode, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.users.disable_totp(user.id, data.code)


@router.get("/oauth/{provider}/login")
def oauth_login(provider: str):
    url, _state = oauth.get_provider(provider).authorization_url()
    return RedirectResponse(url)


@router.get("/oauth/{provider}/callback", response_model=TokenPair)
def oauth_callback(provider: str, code: str, c: Container = Depends(get_container)):
    user = c.users.oauth_login(provider, code)
    c.audit.record(user.id, "user.oauth_login", f"user:{user.id}", provider=provider)
    return c.users.issue_tokens(user)
