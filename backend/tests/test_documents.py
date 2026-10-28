def test_document_crud_and_search(client, auth_headers, workspace):
    h, ws = auth_headers, workspace["id"]
    d = client.post("/api/documents", json={"workspace_id": ws, "title": "Quantum notes",
                                            "content": "Entanglement and superposition"}, headers=h).json()
    client.post("/api/documents", json={"workspace_id": ws, "title": "Recipes", "content": "Pasta with tomatoes"}, headers=h)
    r = client.get("/api/search", params={"workspace_id": ws, "q": "quantum"}, headers=h).json()
    assert r[0]["id"] == d["id"]
    sem = client.get("/api/search/semantic", params={"workspace_id": ws, "q": "superposition entanglement"}, headers=h).json()
    assert sem[0]["id"] == d["id"]
    assert client.patch(f"/api/documents/{d['id']}", json={"content": "x"}, headers=h).json()["content"] == "x"
    assert client.delete(f"/api/documents/{d['id']}", headers=h).status_code == 204


def test_document_project_must_match_workspace(client, auth_headers, workspace):
    r = client.post("/api/documents", json={"workspace_id": workspace["id"], "title": "T", "project_id": "nope"},
                    headers=auth_headers)
    assert r.status_code == 404


def test_memory_and_graph(client, auth_headers, workspace):
    h, ws = auth_headers, workspace["id"]
    m = client.post("/api/memory", json={"workspace_id": ws, "content": "The user prefers dark mode"}, headers=h).json()
    assert "embedding" not in m
    hits = client.get("/api/memory/recall", params={"workspace_id": ws, "query": "dark mode"}, headers=h).json()
    assert hits[0]["memory"]["id"] == m["id"]
    a = client.post("/api/memory/entities", json={"workspace_id": ws, "name": "A"}, headers=h).json()
    b = client.post("/api/memory/entities", json={"workspace_id": ws, "name": "B"}, headers=h).json()
    assert client.post("/api/memory/relationships", json={"workspace_id": ws, "source_id": a["id"], "target_id": b["id"]},
                       headers=h).status_code == 201
    assert client.post("/api/memory/relationships", json={"workspace_id": ws, "source_id": a["id"], "target_id": "x"},
                       headers=h).status_code == 404
    g = client.get("/api/memory/graph", params={"workspace_id": ws}, headers=h).json()
    assert len(g["entities"]) == 2 and len(g["relationships"]) == 1
    assert client.delete(f"/api/memory/{m['id']}", headers=h).status_code == 204


def test_embeddings_endpoint(client, auth_headers):
    r = client.post("/api/embeddings", json={"texts": ["a", "b"]}, headers=auth_headers).json()
    assert len(r["embeddings"]) == 2 and r["dimensions"] == 256
