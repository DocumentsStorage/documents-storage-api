from fastapi.testclient import TestClient
from documents_storage_api.main import app


client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_login(get_authorization_header):
    assert "Authorization" in get_authorization_header

def test_bad_login():
    username="WrongUsername"
    password="WrongPassword"
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'username={username}&password={password}')
    assert response.status_code == 403


def test_update_token(get_authorization_header):
    response = client.post(f"/token/update", headers={**get_authorization_header})
    assert response.status_code == 200


def test_bad_update_token():
    response = client.post(f"/token/update", headers={'Authorization': 'bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiI2MjA1NTMwZGM3ZGM2YmE5ZTJmYTg0YTAiLCJyYW5rIjoiYWRtaW4iLCJleHAiOjE2NDQ1MjE1MTB9.Ptl2b-CaClxTouKdPJVlvY1vq0Ot6wTsFK21t1XJvPw'})
    assert response.status_code == 403