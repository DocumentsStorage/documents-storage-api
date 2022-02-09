from fastapi.testclient import TestClient
from documents_storage_api.main import app


client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_login(get_authorization_header):
    assert "Authorization" in get_authorization_header
