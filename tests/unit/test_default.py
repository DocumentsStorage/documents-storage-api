from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest

client = TestClient(app)


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_login(get_authorization_header):
    assert "Authorization" in get_authorization_header
