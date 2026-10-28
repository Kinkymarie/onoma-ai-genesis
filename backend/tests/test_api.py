import os

os.environ["DATABASE_URL"] = "sqlite://"

import pyotp
from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


def _auth(c, email="a@example.com"):
    c.post("/auth/register", json={"email": email, "password": "password123"})
    r = c.post("/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.text
    return r.json()


def test_health():
    with _client() as c:
        assert c.get("/api/health").status_code == 200
        assert c.get("/api/health/db").json() == {"database": "ok"}


def test_auth_flow_refresh_logout():
    with _client() as c:
        t = _auth(c)
        h = {"Authorization": "Bearer " + t["access_token"]}
        assert c.get("/api/projects", headers=h).status_code == 200
        assert c.get("/api/projects").status_code == 401
        r2 = c.post("/auth/refresh", json={"refresh_token": t["refresh_token"]})
        assert r2.status_code == 200
        assert c.post("/auth/refresh", json={"refresh_token": t["refresh_token"]}).status_code == 401
        assert c.post("/auth/logout", headers=h).status_code == 200
        assert c.get("/api/projects", headers=h).status_code == 401


def test_bad_login():
    with _client() as c:
        _auth(c, "b@example.com")
        r = c.post("/auth/login", json={"email": "b@example.com", "password": "wrongpass1"})
        assert r.status_code == 401


def test_2fa():
    with _client() as c:
        t = _auth(c, "c@example.com")
        h = {"Authorization": "Bearer " + t["access_token"]}
        secret = c.post("/auth/2fa/setup", headers=h).json()["secret"]
        assert c.post("/auth/2fa/verify", headers=h, json={"code": pyotp.TOTP(secret).now()}).status_code == 200
        bad = c.post("/auth/login", json={"email": "c@example.com", "password": "password123"})
        assert bad.status_code == 401
        ok = c.post("/auth/login", json={"email": "c@example.com", "password": "password123",
                                          "totp_code": pyotp.TOTP(secret).now()})
        assert ok.status_code == 200


def test_chat_and_agents():
    with _client() as c:
        t = _auth(c, "d@example.com")
        h = {"Authorization": "Bearer " + t["access_token"]}
        c.post("/api/embeddings/batch", headers=h, json={"texts": ["postgres connection pooling"]})
        r = c.post("/api/agents/research", headers=h, json={"input": "postgres pooling", "provider": "local"})
        assert r.status_code == 200 and r.json()["citations"]
        assert c.post("/api/chat", headers=h, json={"message": "hi", "provider": "local"}).status_code == 200
        assert len(c.get("/api/chat/history", headers=h).json()) == 2
        assert c.post("/api/agents/nope/execute", headers=h, json={"input": "x"}).status_code == 404


def test_password_reset():
    from app.models import PasswordResetToken
    from app.database import SessionLocal
    from app.auth.jwt import hash_token
    from datetime import timedelta
    from app.models import utcnow, User
    with _client() as c:
        _auth(c, "e@example.com")
        with SessionLocal() as db:
            u = db.query(User).filter_by(email="e@example.com").one()
            db.add(PasswordResetToken(user_id=u.id, token_hash=hash_token("tok"), expires_at=utcnow() + timedelta(hours=1)))
            db.commit()
        assert c.post("/auth/reset-password", json={"token": "tok", "new_password": "newpassword1"}).status_code == 200
        assert c.post("/auth/reset-password", json={"token": "tok", "new_password": "newpassword2"}).status_code == 400
        assert c.post("/auth/login", json={"email": "e@example.com", "password": "newpassword1"}).status_code == 200
