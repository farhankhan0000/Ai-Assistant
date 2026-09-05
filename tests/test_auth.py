def test_successful_user_registration(client):
    new_user = {
        "email": "testrunner@exampl.com",
        "name" : "Test_User",
        "password" : "weakpassword123"
    }
    response = client.post("/auth/register", json=new_user)

    assert response.status_code == 201