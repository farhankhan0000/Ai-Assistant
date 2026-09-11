import  pytest
import uuid

@pytest.fixture()
def auth_headers(client):
    user_data = {
        "email" : f"test_{uuid.uuid4().hex[:8]}@gmail.com",
        "name" : "sayMyName",
        "password" : "strongPassword"
    }

    user_register = client.post("/auth/register", json=user_data)

    assert user_register.status_code == 201

    login_data = {
        "username" : user_data["email"],
        "password" : user_data["password"]
    }

    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization" : f"Bearer{token}"}


