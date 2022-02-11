from fastapi.testclient import TestClient
from documents_storage_api.main import app
from bson.objectid import ObjectId as BsonObjectId
import pytest
client = TestClient(app)

def get_authorization_header_user(username, password):
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'username={username}&password={password}')
    assert response.status_code == 200
    res = response.json()
    if 'token_type' in res:
        return {"Authorization": res['token_type'] + " " + res['access_token']}
    else:
        return {"Authorization": res['access_token']}

# Tests

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

def test_bad_account_session():
    response = client.get(
        "/accounts/session",
        headers={"Content-Type": "application/json", 'Authorization': 'bearer eyJ0eXAiOiJKv1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiI2MjA1NTMwZGM3ZGM2YmE5ZTJmYTg0YTAiLCJyYW5rIjoiYWRtaW4iLCJleHAiOjE2NDQ1MjE1MTB9.Ptl2b-CaClxTouKdPJVlvY1vq0Ot6wTsFK21t1XJvPw'},
    )
    assert response.status_code == 401


def test_account_list(get_authorization_header):
    response = client.get(
        "/accounts/list?limit=1",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    account = response.json()[0]
    for field in ['_id', 'username', 'rank', 'new_account']:
        assert field in account


def test_account_add(get_authorization_header, username="not_exisitng_0"):
    response = client.post(
        "/accounts",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "username": username,
            "new_password": "exampletest",
            "rank": "user"
        }
    )
    assert response.status_code == 201
    return response.json()

def test_bad_account_add_already_existing(get_authorization_header, username="not_exisitng_0"):
    response = client.post(
        "/accounts",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "username": username,
            "new_password": "exampletest",
            "rank": "user"
        }
    )
    assert response.status_code == 403
    return response.json()

def test_bad_account_add_not_enough_permissions():
    response = client.post(
        "/accounts",
        headers={"Content-Type": "application/json", **get_authorization_header_user("not_exisitng_0", "exampletest")},
        json={
            "username": "x",
            "new_password": "exampletest",
            "rank": "user"
        }
    )
    assert response.status_code == 403


def test_account_remove(get_authorization_header):
    account_id = test_account_add(get_authorization_header, "not_existing_1")['id']["$oid"]
    print(account_id)
    response = client.delete(
        f"/accounts/{account_id}",
        headers={"Content-Type": "application/json", **get_authorization_header}
    )
    assert response.status_code == 200

def test_bad_account_remove_not_existing(get_authorization_header):
    response = client.delete(
        f"/accounts/{BsonObjectId()}",
        headers={"Content-Type": "application/json", **get_authorization_header}
    )
    assert response.status_code == 404


def test_account_update_as_admin(get_authorization_header):
    account_id = test_account_add(get_authorization_header, "not_existing_2")['id']["$oid"]
    response = client.patch(
        f"/accounts/{account_id}",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "username": "newpassword",
            "password": "exampletest",
            "new-password": "new-password",
            "rank": "user"
        }
    )
    assert response.status_code == 200

def test_bad_account_update_as_admin_not_existing(get_authorization_header):
    response = client.patch(
        f"/accounts/{BsonObjectId()}",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "username": "not_exisitng_10",
            "password": "exampletest",
            "new-password": "new-password",
            "rank": "user"
        }
    )
    assert response.status_code == 404


def test_get_notifications(get_authorization_header):
    response = client.get(
        "/accounts/session/notifications",
        headers={"Content-Type": "application/json", **get_authorization_header}
    )
    assert response.status_code == 200