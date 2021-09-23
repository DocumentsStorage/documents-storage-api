from json import loads
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.param_functions import Path, Query
from fastapi.params import Body
from starlette.responses import JSONResponse
from middlewares.require_auth import UserChecker
from models.common import PydanticObjectId
from models.tag.api import CreateTagModel
from models.tag.base import TagModel
from models.tag.responses import NoTagsFoundResponse, SomeTagsNotFoundResponse, TagDeletionResponse, TagUpdatedResponse


router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    dependencies=[Depends(UserChecker)],
)


@router.get("/",
            responses={
                200: {"description": "Tag was found"},
                404: {"model": SomeTagsNotFoundResponse}
            })
async def get_tags_by_ids(tags_ids: List[PydanticObjectId] = Query(None)):
    tags = loads(TagModel.objects(id__in=tags_ids).to_json())
    if len(tags) > 0:
        return JSONResponse(status_code=200, content={"tags": tags})
    else:
        raise HTTPException(404, {"message": SomeTagsNotFoundResponse().message})


@router.get("/list",
            responses={
                200: {"description": "Returned tags"},
                404: {"model": NoTagsFoundResponse}
            })
async def get_tags_list(skip: int = 0, limit: int = 30):
    tags_list = loads(TagModel.objects()[skip:skip + limit].to_json())
    return JSONResponse(status_code=200, content={"tags": tags_list})


@router.post("", responses={
    201: {"description": "Successfully added media files"},
})
async def add_tag(
    tag: CreateTagModel = Body(...)
):
    tag = TagModel(name=tag.name)
    tag = tag.save()
    tag_id = loads(tag.to_json())["_id"]
    return JSONResponse(status_code=201, content={"id": tag_id})


@router.put("/{tag_id}",
            responses={200: {"model": TagUpdatedResponse},
                       404: {"model": NoTagsFoundResponse}})
async def update_document(
    name: str,
    tag_id: PydanticObjectId = Path(..., title="The ID of the tag to update")
):
    updated = TagModel.objects(id=tag_id).update(name=name)
    if updated == 1:
        return {"message": TagUpdatedResponse().message}
    else:
        raise HTTPException(404, NoTagsFoundResponse().message)


@router.delete("/{tag_id}",
               responses={
                   200: {"model": TagDeletionResponse},
                   404: {"model": SomeTagsNotFoundResponse}
               })
async def delete_tags(
        tag_id: PydanticObjectId = Path(..., title="The ID of the tag to delete")
):
    deleted_tags = TagModel.objects(id=tag_id).delete()
    if deleted_tags == 1:
        return JSONResponse(status_code=200, content={"message": TagDeletionResponse().message})
    else:
        raise HTTPException(404, detail={"message": NoTagsFoundResponse().message()})
