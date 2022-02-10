import os
from fastapi.testclient import TestClient
from documents_storage_api.main import app
import uuid
import pytest
client = TestClient(app)


@pytest.fixture
def media_add(get_authorization_header):
    MEDIA_FILES_PATH = os.getcwd() + "/tests/example_media_files/"

    files = []
    for media_file in os.scandir(MEDIA_FILES_PATH):
        print(media_file.name)
        files.append(('media_files', (media_file.name, open(media_file.path, 'rb'))))

    response = client.post(
        "/media",
        headers={**get_authorization_header},
        files=files
    )
    assert response.status_code == 201
    return response.json()['ids']


def media_delete(get_authorization_header, multiple_media_id):
    query = "/media?"
    for index, id in enumerate(multiple_media_id):
        if index != 0:
            query += "&"
        query += "media_files_ids="+id
    response = client.delete(
        query,
        headers={"Content-Type": "application/json", **get_authorization_header}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Media file successfully deleted"}
    return True


# Tests

def test_media_add(get_authorization_header, media_add):
    assert len(media_add) > 0
    assert media_delete(get_authorization_header, media_add)


def test_media_single_get(get_authorization_header, media_add):
    single_media_id = media_add[0]
    response = client.get(
        f'/media/{single_media_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 200
    assert media_delete(get_authorization_header, media_add)

def test_bad_media_single_get(get_authorization_header):
    single_media_id = str(uuid.uuid4())
    response = client.get(
        f'/media/{single_media_id}',
        headers={"Content-Type": "application/json", **get_authorization_header},
    )
    assert response.status_code == 404


def test_media_delete(get_authorization_header, media_add):
    assert media_delete(get_authorization_header, media_add)


def test_bad_media_delete(get_authorization_header):
    response = client.delete(
        f"/media?media_files_ids={uuid.uuid4()}",
        headers={"Content-Type": "application/json", **get_authorization_header}
    )
    assert response.status_code == 404