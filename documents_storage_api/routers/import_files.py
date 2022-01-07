import io
import os
import pathlib
import shutil
import tarfile
from shutil import copytree
from json import load
from datetime import datetime
from mongoengine import BulkWriteError
from fastapi import APIRouter, Depends, File, UploadFile, Response
from bson.objectid import ObjectId as BsonObjectId
from models.account.base import AccountModel, AccountModelAPI, NotificationModel, NotificationModelAPI
from middlewares.require_auth import PermissionsChecker, UserChecker, UserCheckerModel
from models.common import UUIDFromString
from models.document.base import DocumentFieldModel, DocumentModel


MEDIA_FILES_PATH = os.getcwd() + "/data/media_files/"
TEMP_PATH = os.getcwd() + "/data/temp/"
EXTRACTED_TAR_FILE_PATH = pathlib.Path(TEMP_PATH, "import")


router = APIRouter(
    prefix="/import",
    tags=["import"]
)


def extract_archive(archive_bytes):
    try:
        pathlib.Path(MEDIA_FILES_PATH).mkdir(parents=True, exist_ok=True)
        pathlib.Path(EXTRACTED_TAR_FILE_PATH).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)

    file = tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz")
    file.extractall(EXTRACTED_TAR_FILE_PATH)

# Parse json documents to mongoengine models

def create_document_field_object(document_field_obj):
    return DocumentFieldModel(
        name=document_field_obj['name'],
        value=document_field_obj['value']
    )

def create_document_object(document_obj):
    document = DocumentModel(
        _id=BsonObjectId(document_obj['_id']['$oid']),
        creation_date = datetime.fromtimestamp(document_obj['creation_date']['$date'] / 1000),
        ngrams=document_obj['ngrams'],
        title=document_obj['title'],
        description=document_obj['description'],
        tags=document_obj['tags'],
        media_files=(UUIDFromString([uuid_string['$uuid']])[0] for uuid_string in document_obj['media_files']),
        fields=[create_document_field_object(field) for field in document_obj['fields']]
    )
    if 'modification_date' in document_obj:
        document.modification_date = datetime.fromtimestamp(document_obj['modification_date']['$date'] / 1000)
    return document

def create_notification_object(notification_obj: NotificationModelAPI):
    return NotificationModel(
        text=notification_obj['text'],
        creation_date=datetime.fromtimestamp(notification_obj['creation_date']['$date'] / 1000),
        seen=notification_obj['seen']
    )

def create_account_object(account_obj: AccountModelAPI):
    return AccountModel(
                    _id=BsonObjectId(account_obj['_id']['$oid']),
                    username=account_obj['username'],
                    password=account_obj['password'],
                    rank=account_obj['rank'],
                    new_account=account_obj['new_account'],
                    notifications=[create_notification_object(notification) for notification in account_obj['notifications']]
                )



@router.post("/documents", responses={
    200: {"description": "Successfully imported data"},
})
async def import_media_file(
    archive_file: UploadFile = File(...),
    import_documents: bool = True,
    import_images: bool = True,
):
    '''
    Upload documents with media files
    '''
    extract_archive(archive_file.file.read())
    if import_images:
        copytree(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "media_files"), str(pathlib.Path(MEDIA_FILES_PATH)), dirs_exist_ok=True)
    if import_documents:
        with open(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "documents.json"), "r") as documents_file:
            documents = load(documents_file)
            documents_to_save = [create_document_object(document) for document in documents]
            try:
                DocumentModel.objects.insert(documents_to_save)
            except BulkWriteError as bulkErr:
                print(bulkErr)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                return Response(status_code=422)
            except Exception as e:
                print(e)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                return Response(status_code=400)
        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
    return Response(status_code=200)
    



@router.post("/accounts", responses={
    200: {"description": "Successfully imported data"},
})
async def import_media_file(
    archive_file: UploadFile = File(...),
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Upload accounts archive
    '''
    extract_archive(archive_file.file.read())

    if PermissionsChecker("admin", user['rank']):
        with open(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "accounts.json"), "r") as accounts_file:
            accounts = load(accounts_file)
            accounts_to_save = [create_account_object(account) for account in accounts]
            try:
                AccountModel.objects.insert(accounts_to_save)
            except BulkWriteError as bulkErr:
                print(bulkErr)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                return Response(status_code=422)
            except Exception as e:
                print(e)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                return Response(status_code=400)
        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
        return Response(status_code=200)
    else:
        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
        return Response(status_code=403)
