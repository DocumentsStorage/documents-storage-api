import io
import os
import threading
import pathlib
import shutil
import tarfile
from shutil import copytree
from json import load
from bson.objectid import ObjectId
from datetime import datetime
from mongoengine import BulkWriteError
from fastapi import APIRouter, Depends, File, UploadFile, Response
from bson.objectid import ObjectId as BsonObjectId
from models.account.base import AccountModel, AccountModelAPI, NotificationModel, NotificationModelAPI
from middlewares.require_auth import PermissionsChecker, UserChecker, UserCheckerModel
from models.common import PydanticObjectId, UUIDFromString
from models.document.base import DocumentFieldModel, DocumentModel
from services.paths import MEDIA_FILES_PATH, TEMP_PATH

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
    for entry in file:
        if os.path.isabs(entry.name) or ".." in entry.name:
            raise ValueError("Illegal tar archive entry")
    file.extractall(EXTRACTED_TAR_FILE_PATH)

# Parse json documents to mongoengine models

def create_document_field_object(document_field_obj):
    return DocumentFieldModel(
        name=document_field_obj['name'],
        value=document_field_obj['value']
    )

def create_document_object_mongo(document_obj):
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

def create_notification_object_mongo(notification_obj: NotificationModelAPI):
    return NotificationModel(
        text=notification_obj['text'],
        creation_date=datetime.fromtimestamp(notification_obj['creation_date']['$date'] / 1000),
        seen=notification_obj['seen']
    )

def create_account_object_mongo(account_obj: AccountModelAPI):
    return AccountModel(
                    _id=BsonObjectId(account_obj['_id']['$oid']),
                    username=account_obj['username'],
                    password=account_obj['password'],
                    rank=account_obj['rank'],
                    new_account=account_obj['new_account'],
                    notifications=[create_notification_object_mongo(notification) for notification in account_obj['notifications']]
                )

# Import threads

def import_documents(account_id_to_notify: PydanticObjectId, archive_file, import_images: bool, import_overwrite: bool):
    extract_archive(archive_file.file.read())
    if import_images:
        copytree(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "media_files"), str(pathlib.Path(MEDIA_FILES_PATH)), dirs_exist_ok=True)
    if import_documents:
        with open(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "documents.json"), "r") as documents_file:
            documents = load(documents_file)
            try:
                if(import_overwrite):
                    try:
                        for doc in documents:
                            DocumentModel.objects(_id=doc['_id']['$oid']).update(__raw__={'$set': {
                                    'creation_date': datetime.fromtimestamp(doc['creation_date']['$date'] / 1000),
                                    'ngrams': doc['ngrams'],
                                    'title': doc['title'],
                                    'description': doc['description'],
                                    'tags': doc['tags'],
                                    'media_files': [UUIDFromString([uuid_string['$uuid']])[0] for uuid_string in doc['media_files']],
                                    'fields': doc['fields']
                            }}, upsert=True)
                    except Exception as ex:
                        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                else:
                    try:
                        documents_to_save = [create_document_object_mongo(document) for document in documents]
                        DocumentModel.objects.insert(documents_to_save)
                    except BulkWriteError as bulkErr:
                        print(bulkErr)
                        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                        notification_text = f'Documents could not be imported'
                        AccountModel.objects(_id=ObjectId(account_id_to_notify)).update_one(add_to_set__notifications=NotificationModel(text=notification_text))
            except Exception as e:
                print(e)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                notification_text = f'Documents could not be imported'
                AccountModel.objects(_id=ObjectId(account_id_to_notify)).update_one(add_to_set__notifications=NotificationModel(text=notification_text))
        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
        notification_text = f'Documents were imported'
        AccountModel.objects(_id=ObjectId(account_id_to_notify)).update_one(add_to_set__notifications=NotificationModel(text=notification_text))

def import_accounts(user: AccountModelAPI, archive_file):
    extract_archive(archive_file.file.read())
    if PermissionsChecker("admin", user.rank):
        with open(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "accounts.json"), "r") as accounts_file:
            accounts = load(accounts_file)
            accounts_to_save = [create_account_object_mongo(account) for account in accounts]
            try:
                AccountModel.objects.insert(accounts_to_save)
            except BulkWriteError as bulkErr:
                print(bulkErr)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                notification_text = f'Importing accounts result - Invalid accounts'
                AccountModel.objects(_id=user._id).update_one(add_to_set__notifications=NotificationModel(text=notification_text))
            except Exception as e:
                print(e)
                shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
                notification_text = f'Importing accounts result - Could not import accounts'
                AccountModel.objects(_id=user._id).update_one(add_to_set__notifications=NotificationModel(text=notification_text))
        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
        notification_text = f'Importing accounts result - Imported accounts'
        AccountModel.objects(_id=user._id).update_one(add_to_set__notifications=NotificationModel(text=notification_text))
    else:
        shutil.rmtree(EXTRACTED_TAR_FILE_PATH, ignore_errors = False)
        notification_text = f'Importing accounts result - No sufficient permissions'
        AccountModel.objects(_id=user._id).update_one(add_to_set__notifications=NotificationModel(text=notification_text))



@router.post("/documents", responses={
    200: {"description": "Successfully imported data"},
})
async def import_documents_api(
    user: UserCheckerModel = Depends(UserChecker),
    archive_file: UploadFile = File(...),
    import_documents: bool = True,
    import_images: bool = True,
    import_overwrite: bool = False,
):
    '''
    Upload documents with media files
    '''
    t1 = threading.Thread(target=import_documents_api,
                            kwargs={
                            'account_id_to_notify': user['client_id'],
                            'archive_file': archive_file, 'import_documents': import_documents, 
                            'import_images': import_images, 'import_overwrite': import_overwrite
                            })
    t1.start()
    return Response(status_code=201)



@router.post("/accounts", responses={
    200: {"description": "Successfully imported data"},
})
async def import_accounts_api(
    archive_file: UploadFile = File(...),
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Upload accounts archive
    '''
    t1 = threading.Thread(target=import_accounts, kwargs={'user': user, 'archive_file': archive_file})
    t1.start()
    return Response(status_code=201)
    