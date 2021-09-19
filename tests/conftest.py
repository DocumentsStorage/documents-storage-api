from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest

client = TestClient(app)

username = "admin"
password = "documents-storage-supervisor"


@pytest.fixture
def get_authorization_header():
    response = client.post(
        "/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"},
        data=f'username={username}&password={password}')
    assert response.status_code == 200
    res = response.json()
    return {"Authorization": res['token_type'] + " " + res['access_token']}
