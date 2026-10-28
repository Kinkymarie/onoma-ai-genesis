import pyotp

from app.auth import permissions
from app.auth.password import hash_password, verify_password
from app.utils.validators import validate_password_strength
from app.utils.exceptions import ValidationFailed
import pytest

from .conftest import PASSWORD, bearer, make_user


def test_password_hash_roundtrip():
    h = hash_password("Abcdef12")
    assert verify_password("Abcdef12", h) and not verify_password("nope", h)
    assert not verify_password("x", None)


def test_password_strength():
    with pytest.raises(ValidationFailed):
        validate_password_strength("weak")


def test_rbac():
    assert permissions.has_permission("admin", "admin")
    assert not permissions.has_permission("viewer", "write")


def test_register_login_me(client):
    user, headers, _ = make_user(client)
    assert user["role"] == "admin"
    assert "password_hash" not in user
    assert client.get("/api/auth/me", headers=headers).json()["email"] == "admin@example.com"


def test_duplicate_and_weak_registration(client, admin):
    r = client.post("/api/auth/register", json={"email": "admin@example.com", "name": "x", "password": PASSWORD})
    assert r.status_code == 409
    r = client.post("/api/auth/register", json={"email": "b@example.com", "name": "x", "password": "weak"})
    assert r.status_code == 422


def test_bad_login_and_unauthenticated(client, admin):
    assert client.post("/api/auth/login", json={"email": "admin@example.com", "password": "Wrong1234"}).status_code == 401
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=bearer("garbage")).status_code == 401


def test_refresh_rotation_and_logout(client, admin):
    _, headers, tokens = admin
    r = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    # old refresh token is now revoked
    assert client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    # access token cannot be used as refresh token
    assert client.post("/api/auth/refresh", json={"refresh_token": tokens["access_token"]}).status_code == 401
    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_totp_flow(client, admin):
    _, headers, _ = admin
    uri = client.post("/api/auth/2fa/setup", headers=headers).json()["provisioning_uri"]
    secret = uri.split("secret=")[1].split("&")[0]
    code = pyotp.TOTP(secret).now()
    assert client.post("/api/auth/2fa/confirm", json={"code": code}, headers=headers).json()["totp_enabled"]
    body = {"email": "admin@example.com", "password": PASSWORD}
    assert client.post("/api/auth/login", json=body).status_code == 401
    assert client.post("/api/auth/login", json={**body, "totp_code": pyotp.TOTP(secret).now()}).status_code == 200


def test_change_password(client, admin):
    _, headers, _ = admin
    assert client.post("/api/auth/password", json={"current_password": "bad", "new_password": "NewPassw0rd1"},
                       headers=headers).status_code == 401
    assert client.post("/api/auth/password", json={"current_password": PASSWORD, "new_password": "NewPassw0rd1"},
                       headers=headers).status_code == 200
    assert client.post("/api/auth/login", json={"email": "admin@example.com", "password": "NewPassw0rd1"}).status_code == 200


def test_oauth_unconfigured(client):
    assert client.get("/api/auth/oauth/google/login", follow_redirects=False).status_code == 400
    assert client.get("/api/auth/oauth/nope/login", follow_redirects=False).status_code == 400
