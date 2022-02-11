import uuid
from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest
from bson.objectid import ObjectId as BsonObjectId

client = TestClient(app)


def test_tag_add(get_authorization_header):
    response = client.post(
        "/tags",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "name": "TagName"
        }
    )
    assert response.status_code == 201

def test_tag_list(get_authorization_header):
    response = client.get(
        "/tags/list",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    return response.json()

def test_get_tags_by_ids(get_authorization_header):
    tag_id = test_tag_list(get_authorization_header)['tags'][0]['_id']['$oid']
    response = client.get(
        f"/tags?tags_ids={tag_id}",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200

def test_get_bad_tags_by_ids(get_authorization_header):
    response = client.get(
        f"/tags?tags_ids={BsonObjectId()}",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 404

def test_update_tag(get_authorization_header):
    tag_id = test_tag_list(get_authorization_header)['tags'][0]['_id']['$oid']
    response = client.put(
        f"/tags/{tag_id}?name=NewTagName",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    return response.json()

def test_update_bad_tag(get_authorization_header):
    response = client.put(
        f"/tags/{BsonObjectId()}?name=NewTagName",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 404
    return response.json()


def test_delete_tag(get_authorization_header):
    tag_id = test_tag_list(get_authorization_header)['tags'][0]['_id']['$oid']
    response = client.delete(
        f"/tags/{tag_id}",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200

def test_bad_delete_tag(get_authorization_header):
    response = client.delete(
        f"/tags/{BsonObjectId()}",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 404