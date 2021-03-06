import io
import threading
import os
import pathlib
import uuid
import tarfile
from json import dumps, loads
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Response
from fastapi.params import Query
from starlette.responses import FileResponse
from models.account.base import AccountModel
from models.common import  PydanticObjectId, PydanticUUIDString, UUIDFromString, flat_map
from middlewares.require_auth import PermissionsChecker, UserChecker, UserCheckerModel
from models.document.base import DocumentModel
from routers.documents import StringFromUUID
from services.notifications import add_notification
from services.paths import MEDIA_FILES_PATH, TEMP_PATH


router = APIRouter(
    prefix="/export",
    tags=["export"]
)

def remove_archive_file(file_path):
    print("Trying to remove tempororay file:", file_path)
    try:
        os.remove(file_path)
        print('Removed successfully')
    except OSError as error:
        print(error)
        print("File path cannot be removed")

def build_archive(
    account_id_to_notify: PydanticObjectId,
    accounts: Optional[bool]=False,
    documents: Optional[dict]=None,
    media_files_ids: Optional[list]=None
):
    try:
        pathlib.Path(TEMP_PATH).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)
    
    file_id = str(uuid.uuid4())
    file_path = pathlib.Path(TEMP_PATH, f"{file_id}.tar.gz")
    with tarfile.open(file_path, "w:gz") as tar:
        # Accounts file
        if accounts:
            json_string = str(AccountModel.objects().to_json()).encode('utf-8')
            json_bytes = io.BytesIO(json_string)
            info = tarfile.TarInfo(name="accounts.json")
            info.size = len(json_string)
            tar.addfile(tarinfo=info, fileobj=json_bytes)

        # Documents file
        if documents:
            json_string = dumps(documents).encode('utf-8')
            json_bytes = io.BytesIO(json_string)
            info = tarfile.TarInfo(name="documents.json")
            info.size = len(json_string)
            tar.addfile(tarinfo=info, fileobj=json_bytes)

        # Media files
        if media_files_ids:
            for entry in os.scandir(MEDIA_FILES_PATH):
                for id in media_files_ids:
                    if str(pathlib.Path(entry.name).with_suffix('')) == str(id):
                        tar.add(entry.path, arcname=str(pathlib.Path("media_files", str(pathlib.Path(entry.name)))))

    file_url = f'http://{os.getenv("HOST_IP")}:{os.getenv("API_PORT")}/export/{file_id}'
    add_notification(account_id_to_notify,  f'Archived files are available for 24 hours since this notification has been added, downloaded from: {file_url}')
    t1 = threading.Timer(60*60*24, remove_archive_file, [file_path])
    t1.start()


@router.post("/accounts",
             responses={
                 200: {"description": "Started creating archive"},
             }
             )
async def start_accounts_export(
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Export all accounts.
    '''
    if PermissionsChecker("admin", user['rank']):
        t1 = threading.Thread(target=build_archive, kwargs={'account_id_to_notify': user['client_id'], 'accounts': True})
        t1.start()
        return Response(status_code=200)
    else:
        return Response(status_code=403)

@router.post("/documents",
             responses={
                 200: {"description": "Started creating archive"},
             }
             )
async def start_documents_export(
    include_media: bool = True,
    document_ids: List[PydanticObjectId] = Query(None, description="If null, then all documents will be included in export"),
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Export documents with optional include of media files to compressed tar.
    '''
    # Get documents
    if(document_ids is not None):
        documents_from_db = loads(DocumentModel.objects(id__in=document_ids).to_json())
    else:
        documents_from_db = loads(DocumentModel.objects.to_json())
    
    media_files_ids = []
    if include_media:
        for doc in documents_from_db:
            media_files_ids.append(StringFromUUID(doc['media_files']))
        media_files_ids = flat_map(list(map(lambda x: list(map(lambda y: str(y), UUIDFromString(x))), media_files_ids)))
    
    t1 = threading.Thread(target=build_archive, kwargs={'account_id_to_notify': user['client_id'], 'documents': documents_from_db, 'media_files_ids': media_files_ids})
    t1.start()

    return Response(status_code=200)

@router.get("/{file_id}",
             responses={
                 200: {"description": "Downloaded archive successfully"},
             }
             )
async def download_export(
    file_id: PydanticUUIDString = Query(None, description="Id of archive file"),
):
    '''
    Download exported documents (tar.gz file)
    '''
    for entry in os.scandir(TEMP_PATH):
        if str(pathlib.Path(entry.name).with_suffix('')) == file_id+".tar":
            created = os.stat(entry.path).st_ctime
            date = datetime.fromtimestamp(created).strftime("%x-%H_%M")
            return FileResponse(entry.path, filename=f'documents-storage-export-{date}.tar.gz', media_type='application/gzip')
            
            
    