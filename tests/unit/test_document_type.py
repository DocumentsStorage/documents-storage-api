from fastapi.testclient import TestClient
from documents_storage_api.main import app
import pytest

client = TestClient(app)


def test_document_type_add(get_authorization_header):
    response = client.post(
        "/document_types",
        headers={"Content-Type": "application/json", **get_authorization_header},
        json={
            "title": "Invoice",
            "description": "Invoice document",
            "fields": [
                {
                    "name": "Seller name",
                    "value_type": "text"
                },
                {
                    "name": "Buyer name",
                    "value_type": "text"
                },
                {
                    "name": "Date",
                    "value_type": "date"
                },
                {
                    "name": "Total amount",
                    "value_type": "number"
                },
                {
                    "name": "Amount currency",
                    "value_type": "text"
                }
            ]
        }
    )
    assert response.status_code == 201


def test_document_type_list(get_authorization_header):
    response = client.get(
        "/document_types?skip=0&limit=1",
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    document_type = response.json()[0]
    for field in ['_id', 'title', 'description', 'fields']:
        assert field in document_type
    return document_type


def test_document_type_update(get_authorization_header):
    document_type_id = test_document_type_list(get_authorization_header)['_id']['$oid']
    response = client.put(
        f'/document_types/{document_type_id}',
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
    assert response.json() == {"message": "Document type successfully updated"}


def test_document_type_delete(get_authorization_header):
    document_type_id = test_document_type_list(get_authorization_header)['_id']['$oid']
    response = client.delete(
        f'/document_types/{document_type_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document type successfully deleted"}
