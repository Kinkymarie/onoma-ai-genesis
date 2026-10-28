def test_workspace_org_crud(client, auth_headers, workspace):
    h = auth_headers
    org = client.post("/api/organizations", json={"name": "Acme Inc"}, headers=h).json()
    assert org["slug"] == "acme-inc"
    assert client.post("/api/organizations", json={"name": "Other", "slug": "acme-inc"}, headers=h).status_code == 409
    assert client.patch(f"/api/organizations/{org['id']}", json={"name": "Acme"}, headers=h).json()["name"] == "Acme"
    assert client.delete(f"/api/organizations/{org['id']}", headers=h).status_code == 204
    assert client.patch(f"/api/workspaces/{workspace['id']}", json={"description": "d"}, headers=h).json()["description"] == "d"


def test_project_crud(client, auth_headers, workspace):
    h = auth_headers
    p = client.post("/api/projects", json={"workspace_id": workspace["id"], "name": "P1"}, headers=h).json()
    assert client.get("/api/projects", params={"workspace_id": workspace["id"]}, headers=h).json()[0]["id"] == p["id"]
    r = client.patch(f"/api/projects/{p['id']}", json={"status": "archived"}, headers=h)
    assert r.json()["status"] == "archived"
    assert client.patch(f"/api/projects/{p['id']}", json={"status": "bogus"}, headers=h).status_code == 422
    assert client.delete(f"/api/projects/{p['id']}", headers=h).status_code == 204
    assert client.get(f"/api/projects/{p['id']}", headers=h).status_code == 404


def test_workspace_isolation(client, admin, member, workspace):
    p = client.post("/api/projects", json={"workspace_id": workspace["id"], "name": "P"}, headers=admin[1]).json()
    assert client.get(f"/api/projects/{p['id']}", headers=member[1]).status_code == 403
    assert client.get("/api/projects", params={"workspace_id": workspace["id"]}, headers=member[1]).status_code == 403
    assert client.post("/api/projects", json={"workspace_id": workspace["id"], "name": "X"},
                       headers=member[1]).status_code == 403
    client.post(f"/api/workspaces/{workspace['id']}/members", json={"user_id": member[0]["id"]}, headers=admin[1])
    assert client.get(f"/api/projects/{p['id']}", headers=member[1]).status_code == 200
    assert client.get("/api/workspaces", headers=member[1]).json()[0]["id"] == workspace["id"]


def test_tasks(client, auth_headers, workspace, admin, member):
    h, ws = auth_headers, workspace["id"]
    t = client.post("/api/tasks", json={"workspace_id": ws, "title": "T", "priority": "high"}, headers=h).json()
    client.post("/api/tasks", json={"workspace_id": ws, "title": "Done", "status": "done"}, headers=h)
    assert len(client.get("/api/tasks", params={"workspace_id": ws, "status": "todo"}, headers=h).json()) == 1
    assert client.patch(f"/api/tasks/{t['id']}", json={"status": "done"}, headers=h).json()["status"] == "done"
    bad = client.post("/api/tasks", json={"workspace_id": ws, "title": "X", "assignee_id": member[0]["id"]}, headers=h)
    assert bad.status_code == 400
    assert client.post("/api/tasks", json={"workspace_id": ws, "title": "X", "priority": "meh"}, headers=h).status_code == 422
