import os
import uuid
from typing import List
import pathlib
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from middlewares.require_auth import UserChecker

MEDIA_FILES_PATH = os.getcwd() + "/data/media_files/"

router = APIRouter(
    prefix="/media",
    tags=["media"],
    dependencies=[Depends(UserChecker)],
    responses={404: {"description": "Not found"}}
)


@router.get("/{media_id}")
async def get_single_media_file(media_id):
    for entry in os.scandir(MEDIA_FILES_PATH):
        if str(pathlib.Path(entry.name).with_suffix('')) == media_id:
            return FileResponse(MEDIA_FILES_PATH + entry.name)
    raise HTTPException(404, "Not found media file")


@router.post("")
async def add_media_files(media_files: List[UploadFile] = File(...)):
    try:
        pathlib.Path(MEDIA_FILES_PATH).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)

    media_files_ids = []
    for media_file in media_files:
        media_file_id = uuid.uuid4()
        file_extension = pathlib.Path(media_file.filename).suffix
        file_name = MEDIA_FILES_PATH + str(media_file_id) + file_extension
        with open(file_name, 'wb+') as f:
            f.write(media_file.file.read())
            f.close()
        media_files_ids.append(media_file_id)
    return {"ids": media_files_ids}


@router.delete("")
async def delete_media_files(media_files_ids: List[str]):
    for entry in os.scandir(MEDIA_FILES_PATH):
        for media_file_id in media_files_ids:
            if str(pathlib.Path(entry.name).with_suffix('')) == media_file_id:
                media_files_ids.remove(media_file_id)
                os.remove(entry.path)

    if len(media_files_ids) == 0:
        return {"deleted": True}

    raise HTTPException(404, f'Not found media files: {media_files_ids}')
