import pytest
from assistant.models import Message, MemoryFact




def test_chat_unauthorized(client):
    chat_payload = {
        "content": "User Message"
    }
    response = client.post("/chat", json=chat_payload)
    assert response.status_code == 401




def test_chat(client,auth_headers,monkeypatch,db):
    monkeypatch.setattr("assistant.routers.chat.get_ai_response",
                        lambda* args, **kwargs: "AI Message")
    monkeypatch.setattr("assistant.routers.chat.get_memory_facts",
                        lambda* args, **kwargs: [{"key" : "favorite colour", "value" : "blue"}])
    monkeypatch.setattr("assistant.routers.chat.get_vector",
                        lambda* args, **kwargs:  [0.0] * 3072 )

    conv_response = client.post("/conversation", json={"title" : "New Chat"}, headers=auth_headers)
    assert conv_response.status_code == 201

    conversation_id = conv_response.json()["id"]

    chat_payload = {
        "content" : "User Message",
        "conversation_id" : conversation_id
    }

    chat_response = client.post("/chat",headers=auth_headers,json=chat_payload)

    assert chat_response.status_code == 201
    assert chat_response.json()["ai_reply"] == "AI Message"

    saved_messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    assert len(saved_messages) == 2
    assert saved_messages[0].content == "User Message"
    assert saved_messages[1].content == "AI Message"

    saved_facts = db.query(MemoryFact).all()
    assert len(saved_facts) == 1
    assert saved_facts[0].key == "favorite colour"
    assert saved_facts[0].value == "blue"

    get_chat_response = client.get(f"/chat/{conversation_id}", headers=auth_headers)
    assert get_chat_response.status_code == 200
    assert get_chat_response.json()[0]["content"] == "User Message"

    get_chat_response_failed = client.get("/chat/234",headers=auth_headers)
    assert get_chat_response_failed.status_code == 404
    assert get_chat_response_failed.json()["detail"] == "Conversation not found"