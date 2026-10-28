from .conftest import make_user


def test_list_users_admin_only(client, admin, member):
    assert len(client.get("/api/users", headers=admin[1]).json()) == 2
    assert client.get("/api/users", headers=member[1]).status_code == 403


def test_user_access_control(client, admin, member):
    assert client.get(f"/api/users/{admin[0]['id']}", headers=member[1]).status_code == 403
    r = client.patch(f"/api/users/{member[0]['id']}", json={"name": "New"}, headers=member[1])
    assert r.json()["name"] == "New"
    assert client.patch(f"/api/users/{admin[0]['id']}", json={"name": "Hax"}, headers=member[1]).status_code == 403


def test_role_change_and_viewer_cannot_write(client, admin, member):
    r = client.put(f"/api/users/{member[0]['id']}/role", params={"role": "viewer"}, headers=admin[1])
    assert r.json()["role"] == "viewer"
    # existing access token carries stale role claim; permissions use the DB role
    assert client.post("/api/workspaces", json={"name": "x"}, headers=member[1]).status_code == 403
    assert client.put(f"/api/users/{member[0]['id']}/role", params={"role": "root"}, headers=admin[1]).status_code == 422


def test_audit_log(client, admin, member):
    logs = client.get("/api/audit", headers=admin[1]).json()
    assert any(l["action"] == "user.login" for l in logs)
    assert client.get("/api/audit", headers=member[1]).status_code == 403


def test_notifications(client, admin, member, workspace):
    client.post(f"/api/workspaces/{workspace['id']}/members", json={"user_id": member[0]["id"]}, headers=admin[1])
    notes = client.get("/api/users/me/notifications", headers=member[1]).json()
    assert len(notes) == 1
    r = client.post(f"/api/users/me/notifications/{notes[0]['id']}/read", headers=member[1])
    assert r.json()["read"] is True
    assert client.get("/api/users/me/notifications", params={"unread": True}, headers=member[1]).json() == []


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"
