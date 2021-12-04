import io
from json import loads
from datetime import datetime
import os
import pathlib
from typing import List
import uuid
from fastapi import APIRouter, Depends, Response
from fastapi.params import Query
from starlette.responses import FileResponse
from models.account.base import AccountModel
from models.common import  PydanticObjectId, UUIDFromString, flat_map
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

def build_archive(account_id_to_notify: PydanticObjectId, media_files_ids: list):
    try:
        pathlib.Path(TAR_FILE_PATHS).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)
    
    file_id = str(uuid.uuid4())
    file_path = TAR_FILE_PATHS + file_id + ".tar.gz"
    with tarfile.open(file_path, "w:gz") as tar:
        # JSON file
        json_string = str(DocumentModel.objects().to_json()).encode('utf-8')
        json_bytes = io.BytesIO(json_string)
        info = tarfile.TarInfo(name="file.json")
        info.size = len(json_string)
        tar.addfile(tarinfo=info, fileobj=json_bytes)

        # Media files
        if media_files_ids:
            for entry in os.scandir(MEDIA_FILES_PATH):
                for id in media_files_ids:
                    if str(pathlib.Path(entry.name).with_suffix('')) == str(id):
                        tar.add(entry.path, arcname=str(pathlib.Path(entry.name)))

    file_url = f'http://{os.getenv("API_HOST")}:{os.getenv("API_PORT")}/export/{file_id}'
    notification = f'Archived files are available to be downloaded from: {file_url}'
    AccountModel.objects(id=account_id_to_notify).update_one(add_to_set__notifications=notification)

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
        documents_from_db = loads(DocumentModel.objects(id__in=ids).to_json())
    else:
        documents_from_db = loads(DocumentModel.objects.to_json())
    
    media_files_ids = []
    if include_media:
        for doc in documents_from_db:
            media_files_ids.append(StringFromUUID(doc['media_files']))
        media_files_ids = flat_map(list(map(lambda x: list(map(lambda y: str(y), UUIDFromString(x))), media_files_ids)))
    
    t1 = threading.Thread(target=build_archive, kwargs={'account_id_to_notify': user['client_id'], 'media_files_ids': media_files_ids})
    t1.start()

    return Response(status_code=200)

@router.post("/{file_id}",
             responses={
                 200: {"description": "Downloaded temporary file successfully"},
             }
             )
async def download_bulk_export(
    file_id: str = Query(None, description="Id of archive file"),
):
    '''
    Download exported documents (tar.gz file)
    '''
    for entry in os.scandir(TAR_FILE_PATHS):
        if str(pathlib.Path(entry.name).with_suffix('')) == file_id+".tar":
            created = os.stat(entry.path).st_ctime
            date = datetime.fromtimestamp(created).strftime("%x-%H_%M")
            return FileResponse(entry.path, filename=f'documents-storage-export-{date}.tar.gz', media_type='application/gzip')
            
            
    