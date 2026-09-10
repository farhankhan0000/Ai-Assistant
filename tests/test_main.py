
def test_successful_welcome(client):
    response = client.get("/")

    assert response.status_code == 200

    assert "text/html" in response.headers["content-type"]

    assert "welcome page" in response.text.lower()