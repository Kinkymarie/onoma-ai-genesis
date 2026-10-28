from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import oauth, totp
from ..auth.jwt import (
    blacklist, create_access_token, create_refresh_token, decode_token, hash_token, random_token,
)
from ..auth.password import hash_password, verify_password
from ..database import get_db
from ..dependencies import bearer, get_current_user
from ..email import send_email
from ..models import (
    EmailVerificationToken, OAuthAccount, PasswordResetToken, RefreshToken, User, utcnow,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = ""


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class RefreshIn(BaseModel):
    refresh_token: str


class CodeIn(BaseModel):
    code: str


class EmailIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class OAuthIn(BaseModel):
    token: str


def _issue(db: Session, user: User) -> dict:
    refresh = create_refresh_token(user.id)
    payload = decode_token(refresh, "refresh")
    db.add(RefreshToken(
        user_id=user.id, token_hash=hash_token(payload["jti"]),
        expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc),
    ))
    db.commit()
    return {"access_token": create_access_token(user.id), "refresh_token": refresh, "token_type": "bearer"}


def _make_token(db: Session, model, user: User, hours: int) -> str:
    raw = random_token()
    db.add(model(user_id=user.id, token_hash=hash_token(raw), expires_at=utcnow() + timedelta(hours=hours)))
    db.commit()
    return raw


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _consume(db: Session, model, raw: str) -> User:
    row = db.scalar(select(model).where(model.token_hash == hash_token(raw)))
    if row is None or row.used or _aware(row.expires_at) < utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired token")
    row.used = True
    user = db.get(User, row.user_id)
    db.commit()
    return user


@router.post("/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == body.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(email=body.email.lower(), password_hash=hash_password(body.password), full_name=body.full_name)
    db.add(user)
    db.commit()
    raw = _make_token(db, EmailVerificationToken, user, 24)
    send_email(user.email, "Verify your Onoma account", f"Verification token: {raw}")
    return {"id": user.id, "email": user.email, "message": "Verification email sent"}


@router.post("/verify-email")
def verify_email(body: OAuthIn, db: Session = Depends(get_db)):
    user = _consume(db, EmailVerificationToken, body.token)
    user.email_verified = True
    db.commit()
    return {"verified": True}


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not user.is_active or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if user.totp_enabled:
        if not body.totp_code or not totp.verify_code(user.totp_secret, body.totp_code):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "2FA code required or invalid")
    return _issue(db, user)


@router.post("/refresh")
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token, "refresh")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(payload["jti"])))
    if row is None or row.used:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token revoked")
    row.used = True
    user = db.get(User, int(payload["sub"]))
    db.commit()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid user")
    return _issue(db, user)


@router.post("/logout")
def logout(creds=Depends(bearer), user: User = Depends(get_current_user), body: RefreshIn | None = None,
           db: Session = Depends(get_db)):
    p = decode_token(creds.credentials, "access")
    blacklist(p["jti"], p["exp"])
    if body:
        try:
            r = decode_token(body.refresh_token, "refresh")
            blacklist(r["jti"], r["exp"])
        except jwt.PyJWTError:
            pass
    return {"logged_out": True}


def _oauth_login(db: Session, ident: oauth.OAuthIdentity) -> dict:
    acct = db.scalar(select(OAuthAccount).where(
        OAuthAccount.provider == ident.provider, OAuthAccount.provider_user_id == ident.provider_user_id))
    if acct:
        user = db.get(User, acct.user_id)
    else:
        user = db.scalar(select(User).where(User.email == ident.email.lower()))
        if user is None:
            user = User(email=ident.email.lower(), full_name=ident.name, email_verified=True)
            db.add(user)
            db.commit()
        db.add(OAuthAccount(user_id=user.id, provider=ident.provider, provider_user_id=ident.provider_user_id))
        db.commit()
    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid user")
    return _issue(db, user)


@router.post("/oauth/google")
def oauth_google(body: OAuthIn, db: Session = Depends(get_db)):
    try:
        return _oauth_login(db, oauth.google_identity(body.token))
    except oauth.OAuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))


@router.post("/oauth/github")
def oauth_github(body: OAuthIn, db: Session = Depends(get_db)):
    try:
        return _oauth_login(db, oauth.github_identity(body.token))
    except oauth.OAuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))


@router.post("/2fa/setup")
def setup_2fa(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.totp_enabled:
        raise HTTPException(status.HTTP_409_CONFLICT, "2FA already enabled")
    user.totp_secret = totp.new_secret()
    db.commit()
    return {"secret": user.totp_secret, "otpauth_uri": totp.provisioning_uri(user.totp_secret, user.email)}


@router.post("/2fa/verify")
def verify_2fa(body: CodeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.totp_secret or not totp.verify_code(user.totp_secret, body.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid code")
    user.totp_enabled = True
    db.commit()
    return {"enabled": True}


@router.post("/forgot-password")
def forgot_password(body: EmailIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user:
        raw = _make_token(db, PasswordResetToken, user, 1)
        send_email(user.email, "Reset your Onoma password", f"Reset token: {raw}")
    return {"message": "If the account exists, a reset email was sent"}


@router.post("/reset-password")
def reset_password(body: ResetIn, db: Session = Depends(get_db)):
    user = _consume(db, PasswordResetToken, body.token)
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"reset": True}
