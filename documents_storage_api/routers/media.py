import os
import uuid
from typing import List
import pathlib
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.param_functions import Query
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from middlewares.require_auth import UserChecker
from models.common import PydanticUUIDString, UUIDFromString
from models.media.responses import MediaDeletionResponse, MediaNotFoundResponse
from services.paths import MEDIA_FILES_PATH


router = APIRouter(
    prefix="/media",
    tags=["media"],
    dependencies=[Depends(UserChecker)],
)


@router.get("/{media_id}",
            responses={
                200: {"description": "File was found"},
                404: {"model": MediaNotFoundResponse}
            })
async def get_single_media_file(media_id: PydanticUUIDString):
    media_id = UUIDFromString([media_id])[0]
    for entry in os.scandir(MEDIA_FILES_PATH):
        if str(pathlib.Path(entry.name).with_suffix('')) == str(media_id):
            return FileResponse(pathlib.Path(MEDIA_FILES_PATH, entry.name))
    raise HTTPException(404, {"message": MediaNotFoundResponse().message})


@router.post("", responses={
    201: {"description": "Successfully added media files"},
})
async def add_media_files(
    media_files: List[UploadFile] = File(...)
):
    pathlib.Path(MEDIA_FILES_PATH).mkdir(parents=True, exist_ok=True)

    media_files_ids = []
    for media_file in media_files:
        media_file_id = uuid.uuid4()
        file_extension = pathlib.Path(media_file.filename).suffix
        file_name =  pathlib.Path(MEDIA_FILES_PATH, f"{str(media_file_id)}{file_extension}")
        with open(file_name, 'wb+') as f:
            f.write(media_file.file.read())
            f.close()
        media_files_ids.append((media_file_id.hex))
    return JSONResponse(status_code=201, content={"ids": media_files_ids})


@router.delete("",
               responses={
                   200: {"model": MediaDeletionResponse},
                   404: {"description": "Some media files were not found, in message there is list of not deleted media"}
               })
async def delete_media_files(
    media_files_ids: List[PydanticUUIDString] = Query(None)
):
    media_files_ids = UUIDFromString(media_files_ids)
    for entry in os.scandir(MEDIA_FILES_PATH):
        for id in media_files_ids:
            if str(pathlib.Path(entry.name).with_suffix('')) == str(id):
                media_files_ids.remove(id)
                os.remove(entry.path)

    if len(media_files_ids) == 0:
        return JSONResponse(status_code=200, content={"message": MediaDeletionResponse().message})
    else:
        return JSONResponse(status_code=404, content={"message": 'Not found media files: {media_files_ids}'})
