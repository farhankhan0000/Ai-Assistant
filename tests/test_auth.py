import uuid
import pytest


@pytest.fixture()
def new_user_payload():
    return {
        "email" : f"test_{uuid.uuid4().hex[:8]}@example.com",
        "name" : "Test_User",
        "password" : "weakpassword123"
    }


def test_successful_user_registration(client,new_user_payload):
    response = client.post("/auth/register", json=new_user_payload)

    assert response.status_code == 201


def test_duplicate_user_registration_fails(client, new_user_payload):
    response = client.post("/auth/register", json=new_user_payload)
    assert response.status_code == 201

    duplicate_email_response = client.post("/auth/register", json=new_user_payload)
    assert duplicate_email_response.status_code == 409
    assert duplicate_email_response.json()["detail"] == "Email already registered"

def test_successful_user_login(client, new_user_payload):
    register_response = client.post("/auth/register", json=new_user_payload)

    assert register_response.status_code == 201

    login_data = {
        "username" : new_user_payload["email"],
        "password" : new_user_payload["password"]
    }

    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_failed_user_login_email(client, new_user_payload):
    register_response = client.post("/auth/register", json=new_user_payload)

    assert register_response.status_code == 201

    wrong_data = {
        "username" : "ingapinga",
        "password" : "weakPassword"
    }

    failed_login_response = client.post("/auth/login", data=wrong_data)

    assert failed_login_response.status_code == 401

def test_failed_user_login_password(client, new_user_payload):
    register_user = client.post("/auth/register", json=new_user_payload)

    assert register_user.status_code == 201

    wrong_data = {
        "username" : new_user_payload["email"],
        "password" : "ingapinga"
    }

    login_user = client.post("/auth/login", data=wrong_data)

    assert login_user.status_code == 401
