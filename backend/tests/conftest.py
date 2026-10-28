import os

os.environ.setdefault("BCRYPT_ROUNDS", "4")
os.environ["RATE_LIMIT_PER_MINUTE"] = "0"
os.environ["OPENAI_API_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["STORAGE_PATH"] = "/tmp/onoma-test-storage"

import pytest
from fastapi.testclient import TestClient

from app.auth.jwt import blacklist
from app.dependencies import container
from app.main import app

PASSWORD = "Str0ngPassw0rd"


@pytest.fixture(autouse=True)
def clean_state():
    container.repos.reset()
    blacklist.clear()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def bearer(token):
    return {"Authorization": " ".join(["Bearer", token])}


def make_user(client, email="admin@example.com", name="User"):
    r = client.post("/api/auth/register", json={"email": email, "name": name, "password": PASSWORD})
    assert r.status_code == 201, r.text
    tokens = client.post("/api/auth/login", json={"email": email, "password": PASSWORD}).json()
    return r.json(), bearer(tokens["access_token"]), tokens


@pytest.fixture
def admin(client):
    """First registered user (admin)."""
    return make_user(client)


@pytest.fixture
def member(client, admin):
    return make_user(client, "member@example.com", "Member")


@pytest.fixture
def auth_headers(admin):
    return admin[1]


@pytest.fixture
def workspace(client, auth_headers):
    r = client.post("/api/workspaces", json={"name": "WS"}, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()
