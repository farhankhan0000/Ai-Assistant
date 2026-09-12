import pytest

from sandBox.embedding_practice import response



def test_chat_unauthorized(client):
    chat_payload = {
        "content": "User Message"
    }
    response = client.post("/chat", json=chat_payload)
    assert response.status_code == 401




def test_chat(client,auth_headers,monkeypatch):
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