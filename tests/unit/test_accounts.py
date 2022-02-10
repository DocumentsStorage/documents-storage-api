from fastapi.testclient import TestClient
from documents_storage_api.main import app

client = TestClient(app)


def test_account_session(get_authorization_header):
    response = client.get(
        "/accounts/session",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "admin",
        "rank": "admin",
        "new_account": True,
        "notifications": []
    }


def test_account_list(get_authorization_header):
    response = client.get(
        "/accounts/list?limit=1",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    account = response.json()[0]
    for field in ['_id', 'username', 'rank', 'new_account']:
        assert field in account
