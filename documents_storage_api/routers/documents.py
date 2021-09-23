from datetime import datetime
from json import loads
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from starlette.responses import JSONResponse
from middlewares.require_auth import UserChecker
from models.common import PydanticObjectId, UUIDFromString
from models.document.api import CreateDocumentModel, UpdateDocumentModel
from models.document.base import DocumentModel
from models.document.responses import DocumentDeletionResponse, DocumentNotFoundResponse, DocumentUpdatedResponse
from routers.media import delete_media_files

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(UserChecker)],
)


def StringFromUUID(media_files):
    return list(map(lambda file: str(file['$uuid']), media_files))


# Documents


@router.post("",
             responses={
                 201: {"description": "Successfully created document"},
             }
             )
async def add_document(
    document: CreateDocumentModel
):
    fields = []
    if document.fields:
        for field in document.fields:
            fields.append({
                "name": field.name,
                "value": field.value
            })

    media_files = UUIDFromString(document.media_files) if document.media_files else []

    document_object = DocumentModel(
        creation_date=datetime.now(),
        title=document.title,
        description=document.description,
        tags=document.tags,
        media_files=media_files,
        fields=fields
    )
    document = document_object.save()
    document_id = loads(document.to_json())["_id"]
    return JSONResponse(status_code=201, content={"id": document_id})


@router.put("/{document_id}",
            responses={200: {"model": DocumentUpdatedResponse},
                       404: {"model": DocumentNotFoundResponse}})
async def update_document(
    document: UpdateDocumentModel,
    document_id: PydanticObjectId = Path(..., title="The ID of the document to update")
):
    '''This path allow to - update: title, description and overwrite: tags, fields, media_files'''
    document_object = dict(document)

    # Delete not passed properties
    document_object = {
        key: val for key,
        val in document_object.items() if val is not None}

    # Get previous state of document
    try:
        document_from_db = loads(
            DocumentModel.objects(
                id=document_id)[0].to_json())
    except BaseException:
        raise HTTPException(404, "Not found document")

    tags = []
    for tag in document.tags:
        tags.append(tag)

    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value": field.value
        })

    media_files = []
    if document.media_files:
        if len(document.media_files) == 0:
            media_files = []
        elif document.media_files:
            media_files = UUIDFromString(document.media_files)
        else:
            media_files = StringFromUUID(document_from_db['media_files'])

    # Update dict which will be uploaded to db
    document_from_db.update(document_object)

    DocumentModel.objects(id=document_id).update(
        modification_date=datetime.now(),
        title=document_from_db['title'],
        description=document_from_db['description'],
        set__tags=tags,
        set__media_files=media_files,
        set__fields=fields
    )

    return {"message": DocumentUpdatedResponse().message}


@router.get("",
            responses={200: {"description": "Successfully obtains list of documents"}})
async def get_documents_list(
    skip: int = 0,
    limit: int = 30
):
    '''Get list of documents'''
    documents_list = loads(
        DocumentModel.objects()[skip:skip + limit].to_json())
    return documents_list


@router.delete("/{document_id}",
               responses={200: {"model": DocumentDeletionResponse}, 404: {"model": DocumentNotFoundResponse}})
async def delete_document(
    document_id: PydanticObjectId = Path(..., title="The ID of the document to update")
):
    '''Delete single document'''
    document_object = DocumentModel.objects(id=document_id)
    document_json = loads(document_object.to_json())[0]
    if len(document_json['media_files']) > 0:
        await delete_media_files(StringFromUUID(document_json['media_files']))
    count = document_object.delete()
    if count != 0:
        return JSONResponse(status_code=200, content={"message": DocumentDeletionResponse().message})
    else:
        raise HTTPException(404, {"message": DocumentNotFoundResponse().message})
