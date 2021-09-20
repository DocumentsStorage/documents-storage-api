from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest

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
        "new_account": True
    }


def test_account_add(get_authorization_header):
    response = client.post(
        "/accounts",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "username": "Joh",
            "new_password": "36smA4Sd",
            "rank": "user"
        },
    )
    assert response.status_code == 201


def test_account_list(get_authorization_header):
    response = client.get(
        "/accounts/list?skip=1&limit=1",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    account = response.json()[0]
    for field in ['_id', 'username', 'rank', 'new_account']:
        assert field in account
    return account


def test_account_update(get_authorization_header):
    account_id = test_account_list(get_authorization_header)['_id']['$oid']
    response = client.patch(
        f'/accounts/{account_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "username": "NewUsername",
            "rank": "admin"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Account successfully updated"}


def test_account_delete(get_authorization_header):
    account_id = test_account_list(get_authorization_header)['_id']['$oid']
    response = client.delete(
        f'/accounts/{account_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Account successfully deleted"}
