import io
import os
import pathlib
import tarfile
from json import load
from datetime import datetime
from fastapi import APIRouter, Depends, File, UploadFile, Response
from bson.objectid import ObjectId as BsonObjectId
from models.account.base import AccountModel, AccountModelAPI, NotificationModel, NotificationModelAPI
from middlewares.require_auth import PermissionsChecker, UserChecker, UserCheckerModel

MEDIA_FILES_PATH = os.getcwd() + "/data/media_files/"
TAR_FILE_PATH = os.getcwd() + "/data/temp/"
EXTRACTED_TAR_FILE_PATH = pathlib.Path(TAR_FILE_PATH, "import")

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
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Upload files
    '''
    extract_archive(archive_file.file.read())
    return 200
    



@router.post("/accounts", responses={
    200: {"description": "Successfully imported data"},
})
async def import_media_file(
    archive_file: UploadFile = File(...),
    user: UserCheckerModel = Depends(UserChecker)
):
    '''
    Upload files
    '''
    extract_archive(archive_file.file.read())

    if PermissionsChecker("admin", user['rank']):
        with open(pathlib.Path(EXTRACTED_TAR_FILE_PATH, "accounts.json"), "r") as accounts_file:
            accounts = load(accounts_file)
            accounts_to_save = [create_account_object(account) for account in accounts]
            try:
                AccountModel.objects.insert(accounts_to_save)
            except Exception as e:
                print(e)
                return Response(status_code=400)
        os.rmdir(EXTRACTED_TAR_FILE_PATH)
        return Response(status_code=200)
    else:
        return Response(status_code=403)
