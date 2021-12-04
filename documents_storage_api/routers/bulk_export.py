from json import loads
import os
import pathlib
from typing import List
import uuid
from fastapi import APIRouter, Depends, Response
from fastapi.params import Query
from models.common import  UUIDFromString, flat_map
from middlewares.require_auth import UserChecker, UserCheckerModel
from models.document.base import DocumentModel
import tarfile
from routers.documents import StringFromUUID
import threading

MEDIA_FILES_PATH = os.getcwd() + "/data/media_files/"
TAR_FILE_PATHS = os.getcwd() + "/data/temp/"


router = APIRouter(
    prefix="/export",
    tags=["export"],
    dependencies=[Depends(UserChecker)],
)

def build_archive(account_id_to_notify: str, media_files_ids: list):
    try:
        pathlib.Path(TAR_FILE_PATHS).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)
    file = TAR_FILE_PATHS + str(uuid.uuid4()) + ".tar.gz"
    with tarfile.open(file, "w:gz") as tar:
        for entry in os.scandir(MEDIA_FILES_PATH):
            for id in media_files_ids:
                if str(pathlib.Path(entry.name).with_suffix('')) == str(id):
                    tar.add(entry.path, arcname=str(pathlib.Path(entry.name)))

    # TODO: Add notification through db 
    
@router.post("",
             responses={
                 200: {"description": "Started creating archive"},
             }
             )
async def start_bulk_export(
    include_media: bool = True,
    ids: List[str] = Query(None, description="If null, then all documents will be included in export"),
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Export documents with optional include of media files to compressed tar.
    '''
    # Get documents
    if(ids is not None):
        print("lmao")
        documents_from_db = loads(DocumentModel.objects(id__in=ids).to_json())
    else:
        documents_from_db = loads(DocumentModel.objects.to_json())
    
    if include_media:
        media_files_ids = []
        for doc in documents_from_db:
            media_files_ids.append(StringFromUUID(doc['media_files']))
        media_files_ids = flat_map(list(map(lambda x: list(map(lambda y: str(y), UUIDFromString(x))), media_files_ids)))
        t1 = threading.Thread(target=build_archive, kwargs={'account_id_to_notify': user['client_id'], 'media_files_ids': media_files_ids})
        t1.start()

    return Response(status_code=200)

    # TODO: Add route that will allow to download archived file
