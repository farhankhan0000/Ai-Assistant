import  pytest
import uuid
from datetime import datetime,timedelta,timezone
from jose import jwt
from assistant.routers.auth import SECRET_KEY,algorithm


def test_create_conversation_no_token(client):
    no_response = client.post("/conversation")
    assert no_response.status_code == 401
    assert no_response.json()["detail"] == "Not authenticated"

def test_create_conversation_invalid_token(client):
    bad_header = {"Authorization" : "Bearer header string"}
    failed_response = client.post("/conversation", headers=bad_header)
    assert failed_response.status_code == 401
    assert failed_response.json()["detail"] == "Invalid token"

def test_create_conversation_expired_token(client):
    expired_payload = {
        "id" : 1,
        "email" : "expired_payload@gmail.com",
        "exp" : datetime.now(timezone.utc) - timedelta(minutes=20)
    }
    expired_token = jwt.encode(expired_payload,SECRET_KEY,algorithm=algorithm)
    header = {"Authorization" : f"Bearer {expired_token}"}
    payload = {"title" : "New Chat"}
    response = client.post("/conversation",json=payload, headers=header)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_create_get_edit_delete_conversation(client, auth_headers,monkeypatch):
    monkeypatch.setattr("assistant.routers.conversations.get_ai_title",
                                  lambda content: "AI Generated Title")
    payload = {"title" : "New Chat"}
    create_response = client.post("/conversation", json=payload, headers=auth_headers)
    assert create_response.status_code == 201
    assert create_response.json()["title"] == "New Chat"

    get_response = client.get("/conversation", headers=auth_headers)
    assert get_response.status_code == 200
    conversations = get_response.json()
    assert len(conversations) == 1
    assert conversations[0]["title"] == "New Chat"

    edit_payload = {
        "conversation_id" : conversations[0]["id"],
        "content" : "Explain Relativity Simply"
    }

    edit_response = client.put("/conversation",json=edit_payload, headers=auth_headers)
    assert edit_response.status_code == 200
    assert edit_response.json()["new_title"] == "AI Generated Title"

    delete_response = client.delete(f"/conversation/{conversations[0]["id"]}", headers=auth_headers)
    assert delete_response.status_code == 204