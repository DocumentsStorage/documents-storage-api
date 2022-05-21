from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest

client = TestClient(app)

username = "admin"
password = "test_password"

@pytest.fixture
def get_authorization_header():
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'username={username}&password={password}')
    assert response.status_code == 200
    res = response.json()
    if 'token_type' in res:
        print("WORKS")
        return {"Authorization": res['token_type'] + " " + res['access_token']}
    else:
        print("NOT WORKS")
        return {"Authorization": res['access_token']}