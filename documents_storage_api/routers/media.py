import os
import uuid
import pathlib
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from middlewares.require_auth import UserChecker

router = APIRouter(
    prefix="/media",
    tags=["media"],
    dependencies=[Depends(UserChecker)],
    responses={404: {"description": "Not found"}}
)


@router.post("")
async def add_media_file(media_file: UploadFile = File(...)):
    media_file_id = uuid.uuid4()
    try:
        os.mkdir("media_files")
    except Exception as e:
        print(e)
    file_extension = pathlib.Path(media_file.filename).suffix
    file_name = os.getcwd()+"/media_files/"+str(media_file_id)+file_extension
    with open(file_name, 'wb+') as f:
        f.write(media_file.file.read())
        f.close()
    return {"filename": media_file_id}


@router.delete("")
async def delete_media_file(media_file_id: str = ""):
    for entry in os.scandir(os.getcwd()+"/media_files/"):
        if str(pathlib.Path(entry.name).with_suffix('')) == media_file_id:
            os.remove(entry.path)
            return {"deleted": True}
    raise HTTPException(404, "Not found media file")
