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


# def test_account_add(get_authorization_header):
#     response = client.post(
#         "/accounts",
#         headers={"Content-Type": "application/json", **get_authorization_header},
#         json={
#             "username": "John",
#             "new_password": "36smA4Sd",
#             "rank": "user"
#         }
#     )
    # account = response.json()
    # for field in ['id']:
    #     assert field in account
#     # return account


# def test_account_update(get_authorization_header):
    # account_id = test_account_list(get_authorization_header)['_id']['$oid']
    # response = client.patch(
    #     f'/accounts/{account_id}',
    #     headers={"Content-Type": "application/json", **get_authorization_header}, 
    #     json={
    #         "username": "NewUsername",
    #         "rank": "admin"
    #     }
    # )
    # assert response.status_code == 200
    # assert response.json() == {"message": "Account successfully updated"}


# def test_account_delete(get_authorization_header):
#     account_id = test_account_add(get_authorization_header)["id"]["$oid"]
#     response = client.delete(
#         f'/accounts/{account_id}',
#         headers={"Content-Type": "application/json", **get_authorization_header},
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Account successfully deleted"}
