import json


def test_chat_and_history(client, auth_headers):
    r = client.post("/api/chat", json={"message": "hello"}, headers=auth_headers).json()
    assert r["reply"] == "Echo: hello"
    r2 = client.post("/api/chat", json={"message": "again", "conversation_id": r["conversation_id"]},
                     headers=auth_headers).json()
    conv = client.get(f"/api/chat/conversations/{r2['conversation_id']}", headers=auth_headers).json()
    assert [m["role"] for m in conv["messages"]] == ["user", "assistant", "user", "assistant"]
    assert len(client.get("/api/chat/conversations", headers=auth_headers).json()) == 1


def test_chat_streaming(client, auth_headers):
    with client.stream("POST", "/api/chat/stream", json={"message": "stream me"}, headers=auth_headers) as r:
        lines = [l for l in r.iter_lines() if l.startswith("data:")]
    assert lines[-1] == "data: [DONE]"
    text = "".join(json.loads(l[5:])["content"] for l in lines[:-1] if "content" in l)
    assert text.strip() == "Echo: stream me"


def test_conversations_are_private(client, admin, member):
    cid = client.post("/api/chat", json={"message": "secret"}, headers=admin[1]).json()["conversation_id"]
    assert client.get(f"/api/chat/conversations/{cid}", headers=member[1]).status_code == 404
    assert client.post("/api/chat", json={"message": "x", "conversation_id": cid}, headers=member[1]).status_code == 404


def test_chat_requires_auth_and_valid_input(client, auth_headers):
    assert client.post("/api/chat", json={"message": "x"}).status_code == 401
    assert client.post("/api/chat", json={"message": ""}, headers=auth_headers).status_code == 422
    assert client.post("/api/chat", json={"message": "x", "provider": "nope"}, headers=auth_headers).status_code == 400


def test_chat_with_rag(client, auth_headers, workspace):
    ws = workspace["id"]
    client.post("/api/documents", json={"workspace_id": ws, "title": "Kiwi", "content": "kiwi birds are flightless"},
                headers=auth_headers)
    r = client.post("/api/chat", json={"message": "kiwi", "workspace_id": ws, "use_rag": True}, headers=auth_headers)
    assert r.status_code == 200
