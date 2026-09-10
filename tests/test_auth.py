import uuid



def test_successful_user_registration(client):
    new_user = {
        "email": f"test_{uuid.uuid4().hex[:8]}@exampl.com",
        "name" : "Test_User",
        "password" : "weakpassword123"
    }
    response = client.post("/auth/register", json=new_user)

    assert response.status_code == 201


