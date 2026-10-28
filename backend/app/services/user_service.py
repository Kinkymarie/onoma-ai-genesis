"""User management and authentication logic."""
from __future__ import annotations

from ..auth import jwt as jwt_tokens
from ..auth import oauth, totp
from ..auth.password import hash_password, verify_password
from ..db.repositories import Repositories
from ..models.schemas import TokenPair, User, UserCreate, UserUpdate
from ..utils.exceptions import BadRequest, Conflict, NotFound, Unauthorized

_DUMMY_HASH = hash_password("dummy-password-for-timing")


class UserService:
    def __init__(self, repos: Repositories):
        self.repos = repos

    def register(self, data: UserCreate) -> User:
        if self.repos.users.get_by_email(data.email):
            raise Conflict("Email already registered")
        # The first account becomes the platform admin.
        role = "admin" if self.repos.users.count() == 0 else "member"
        return self.repos.users.create(User(
            email=data.email.lower(), name=data.name, role=role,
            password_hash=hash_password(data.password)))

    def get(self, user_id: str) -> User:
        user = self.repos.users.get(user_id)
        if user is None:
            raise NotFound("User not found")
        return user

    def list(self) -> list[User]:
        return self.repos.users.list()

    def issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(access_token=jwt_tokens.create_access_token(user.id, user.role),
                         refresh_token=jwt_tokens.create_refresh_token(user.id))

    def authenticate(self, email: str, password: str, totp_code: str | None = None) -> User:
        user = self.repos.users.get_by_email(email)
        ok = verify_password(password, user.password_hash if user else _DUMMY_HASH)
        if not user or not ok or not user.is_active:
            raise Unauthorized("Invalid credentials")
        if user.totp_enabled and not totp.verify_code(user.totp_secret, totp_code or ""):
            raise Unauthorized("Invalid or missing 2FA code", code="totp_required")
        return user

    def refresh(self, refresh_token: str) -> TokenPair:
        def role_lookup(uid: str):
            u = self.repos.users.get(uid)
            return u.role if u and u.is_active else None
        access, refresh = jwt_tokens.refresh_tokens(refresh_token, role_lookup)
        return TokenPair(access_token=access, refresh_token=refresh)

    def update(self, user_id: str, data: UserUpdate) -> User:
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in changes:
            changes["email"] = changes["email"].lower()
            existing = self.repos.users.get_by_email(changes["email"])
            if existing and existing.id != user_id:
                raise Conflict("Email already in use")
        self.get(user_id)
        return self.repos.users.update(user_id, **changes)

    def change_password(self, user_id: str, current: str, new: str) -> None:
        user = self.get(user_id)
        if not verify_password(current, user.password_hash):
            raise Unauthorized("Current password is incorrect")
        self.repos.users.update(user_id, password_hash=hash_password(new))

    def set_role(self, user_id: str, role: str) -> User:
        self.get(user_id)
        return self.repos.users.update(user_id, role=role)

    def delete(self, user_id: str) -> None:
        if not self.repos.users.delete(user_id):
            raise NotFound("User not found")

    def begin_totp(self, user_id: str) -> str:
        user = self.get(user_id)
        secret = totp.generate_secret()
        self.repos.users.update(user_id, totp_secret=secret, totp_enabled=False)
        return totp.provisioning_uri(secret, user.email)

    def confirm_totp(self, user_id: str, code: str) -> User:
        user = self.get(user_id)
        if not user.totp_secret:
            raise BadRequest("2FA setup not started")
        if not totp.verify_code(user.totp_secret, code):
            raise BadRequest("Invalid 2FA code")
        return self.repos.users.update(user_id, totp_enabled=True)

    def disable_totp(self, user_id: str, code: str) -> User:
        user = self.get(user_id)
        if not totp.verify_code(user.totp_secret, code):
            raise BadRequest("Invalid 2FA code")
        return self.repos.users.update(user_id, totp_enabled=False, totp_secret=None)

    def oauth_login(self, provider_name: str, code: str) -> User:
        profile = oauth.get_provider(provider_name).fetch_profile(code)
        user = self.repos.users.get_by_email(profile["email"])
        if user is None:
            role = "admin" if self.repos.users.count() == 0 else "member"
            user = self.repos.users.create(User(
                email=profile["email"].lower(), name=profile["name"], role=role,
                is_verified=True, oauth_provider=provider_name))
        if not user.is_active:
            raise Unauthorized("Account disabled")
        return user
