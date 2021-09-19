from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest

client = TestClient(app)


def test_document_add(get_authorization_header):
    response = client.post(
        "/documents",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "Invoice title",
            "description": "Invoice description",
            "fields": [
                {
                    "name": "Seller name",
                    "value": "xox"
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


def test_document_list(get_authorization_header):
    response = client.get(
        "/documents?skip=0&limit=1",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    document_type = response.json()[0]
    for field in ['_id', 'title', 'description', 'fields', 'media_files']:
        assert field in document_type
    return document_type


def test_document_update(get_authorization_header):
    document_id = test_document_list(get_authorization_header)['_id']['$oid']
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
    assert response.json() == {"message": "Document successfully updated"}


def test_document_delete(get_authorization_header):
    document_id = test_document_list(get_authorization_header)['_id']['$oid']
    response = client.delete(
        f'/documents/{document_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document successfully deleted"}
