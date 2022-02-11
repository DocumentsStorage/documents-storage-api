import uuid
from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest
from bson.objectid import ObjectId as BsonObjectId

client = TestClient(app)


def test_document_add(get_authorization_header):
    response = client.post(
        "/tags",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "name": "tagExample1"
        }
    )
    tag_id = response.json()['id']['$oid']
    response = client.post(
        "/documents",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "Invoice title",
            "description": "Invoice description",
            "tags": [tag_id],
            "fields": [
                {
                    "name": "Seller name",
                    "value": "xoxox"
                },
                {
                    "name": "Amount",
                    "value": 4.12
                },
                {
                    "name": "Date",
                    "value": "2021-09-14T14:27:24.000+00:00"
                },
            ],
            "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
        }
    )
    assert response.status_code == 201

def test_document_add_with_empty_title_and_no_text(get_authorization_header):
    response = client.post(
        "/documents",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "",
            "description": "",
            "fields": [
                {
                    "name": "Amount",
                    "value": 4.12
                },
                {
                    "name": "Date",
                    "value": "2021-09-14T14:27:24.000+00:00"
                },
            ],
            "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
        }
    )
    assert response.status_code == 201

def test_document_add_with_empty_title_and_text(get_authorization_header):
    response = client.post(
        "/documents",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "",
            "description": "",
            "fields": [
                {
                    "name": "Seller name",
                    "value": "xoxox"
                },
                {
                    "name": "Amount",
                    "value": 4.12
                },
                {
                    "name": "Date",
                    "value": "2021-09-14T14:27:24.000+00:00"
                },
            ],
            "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
        }
    )
    assert response.status_code == 201


def test_document_add_with_empty_title_and_description_and_empty_text(get_authorization_header):
    response = client.post(
        "/documents",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "",
            "description": "test",
            "fields": [
                {
                    "name": "Amount",
                    "value": 4.12
                },
                {
                    "name": "Date",
                    "value": "2021-09-14T14:27:24.000+00:00"
                },
            ],
            "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
        }
    )
    assert response.status_code == 201


def test_document_search(get_authorization_header):
    response = client.get("/documents",headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 200
    document_type = response.json()['documents'][0]
    for field in ['_id', 'title', 'description', 'fields', 'media_files']:
        assert field in document_type
    return document_type

def test_search_text_document_search(get_authorization_header):
    response = client.get("/documents?search_text=title", headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 200
    document_type = response.json()['documents'][0]
    for field in ['_id', 'title', 'description', 'fields', 'media_files']:
        assert field in document_type
    return document_type

def test_order_by_document_search(get_authorization_header):
    response = client.get("/documents?order_by=Amount", headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 200
    document_type = response.json()['documents'][0]
    for field in ['_id', 'title', 'description', 'fields', 'media_files']:
        assert field in document_type
    return document_type

def test_bad_document_search(get_authorization_header):
    response = client.get("/documents?search_text=none", headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 404


def test_autofill_field(get_authorization_header):
    response = client.get("/documents/autofill?results_for=field&search_text=xoxo", headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 200

def test_autofill_search(get_authorization_header):
    response = client.get("/documents/autofill?results_for=search&search_text=Seller", headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 200

def test_bad_autofill(get_authorization_header):
    response = client.get("/documents/autofill?search_text=thisautofillnotexists", headers={"Content-Type": "application/json", **get_authorization_header})
    assert response.status_code == 404


def test_document_update(get_authorization_header):
    response = client.post(
        "/tags",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "name": "tagExample2"
        }
    )
    tag_id = response.json()['id']['$oid']
    document_id = test_document_search(get_authorization_header)['_id']['$oid']
    response = client.put(
        f'/documents/{document_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "NewTitle",
            "description": "NewDescription",
            "tags": [tag_id],
            "fields": [
                {
                    "name": "OnlyFieldName",
                    "value_type": "text"
                }
            ],
            "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba"]
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document successfully updated", 'title': 'NewTitle'}



def test_bad_document_update(get_authorization_header):
    response = client.put(
        f'/documents/{BsonObjectId()}',
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "NewTitle",
            "description": "NewDescription",
            "tags": [],
            "fields": [
                {
                    "name": "OnlyFieldName",
                    "value_type": "text"
                }
            ]
        }
    )
    assert response.status_code == 404

def test_document_update_without_media(get_authorization_header):
    document_id = test_document_search(get_authorization_header)['_id']['$oid']
    response = client.put(
        f'/documents/{document_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "NewTitle",
            "description": "NewDescription",
            "fields": [
                {
                    "name": "OnlyFieldName",
                    "value_type": "text"
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document successfully updated", 'title': 'NewTitle'}

def test_document_update_with_empty_media(get_authorization_header):
    document_id = test_document_search(get_authorization_header)['_id']['$oid']
    response = client.put(
        f'/documents/{document_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "NewTitle",
            "description": "NewDescription",
            "fields": [
                {
                    "name": "OnlyFieldName",
                    "value_type": "text"
                }
            ],
            "media_files": []
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document successfully updated", 'title': 'NewTitle'}


def test_document_delete(get_authorization_header):
    document_id = test_document_search(get_authorization_header)['_id']['$oid']
    response = client.delete(
        f'/documents/{document_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document successfully deleted"}

def test_bad_document_delete(get_authorization_header):
    response = client.delete(
        f'/documents/{BsonObjectId()}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 404
