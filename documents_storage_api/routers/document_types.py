from json import loads
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from starlette.responses import JSONResponse
from middlewares.require_auth import UserChecker
from models.common import PydanticObjectId
from models.document_type.api import CreateDocumenTypeModel, UpdateDocumentTypeModel
from models.document_type.base import DocumentTypeModel
from models.document_type.responses import (
    DocumentTypeDeletionResponse,
    DocumentTypeTitleTakenResponse,
    DocumentTypeNotFoundResponse,
    DocumentTypeUpdatedResponse)

router = APIRouter(
    prefix="/document_types",
    tags=["document_types"],
    dependencies=[Depends(UserChecker)]
)


@router.post("",
             responses={
                 201: {"description": "Successfully created document type"},
                 403: {"model": DocumentTypeTitleTakenResponse}}
             )
async def add_document_type(
    document_type: CreateDocumenTypeModel
):
    '''Add single document type'''
    fields = []
    for field in document_type.fields:
        fields.append({
            "name": field.name,
            "value_type": field.value_type.value
        })

    document_type_object = DocumentTypeModel.objects(title=document_type.title)
    if not document_type_object:
        document_type = DocumentTypeModel(
            title=document_type.title,
            description=document_type.description,
            fields=fields,
        )
        document_type = document_type.save()
        document_type_id = loads(document_type.to_json())["_id"]
        return JSONResponse(status_code=201, content={"id": document_type_id})
    else:
        raise HTTPException(403, {"message": DocumentTypeTitleTakenResponse().message})


@router.put("/{document_type_id}",
            responses={
                200: {"model": DocumentTypeUpdatedResponse},
                404: {"model": DocumentTypeNotFoundResponse}
            })
async def update_document_type(
    document: UpdateDocumentTypeModel,
    document_type_id: PydanticObjectId = Path(..., title="The ID of the document type to update")
):
    '''This path allow to - update: title, description and overwrite: fields'''
    document_type_object = dict(document)

    # Delete not passed properties
    document_type_object = {
        key: val for key,
        val in document_type_object.items() if val is not None}

    # Get previous state of document
    try:
        document_from_db = loads(
            DocumentTypeModel.objects(
                id=document_type_id)[0].to_json())
    except BaseException:
        raise HTTPException(404, {"message": DocumentTypeNotFoundResponse().message})

    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value_type": field.value_type.value
        })
    # Update dict which will be uploaded to db
    document_from_db.update(document_type_object)

    DocumentTypeModel.objects(id=document_type_id).update(
        title=document_from_db['title'],
        description=document_from_db['description'],
        set__fields=fields
    )

    return JSONResponse(status_code=200, content={"message": DocumentTypeUpdatedResponse().message})


@router.get("",
            responses={
                200: {"description": "Successfully obtains list of document types"},
            })
async def get_document_types_list(
    skip: int = 0,
    limit: int = 10
):
    '''Get list of document types'''
    document_types_list = loads(
        DocumentTypeModel.objects()[skip:skip + limit].to_json())
    return document_types_list


@router.delete("/{document_type_id}",
               responses={
                   200: {"model": DocumentTypeDeletionResponse},
                   404: {"model": DocumentTypeNotFoundResponse}
               })
async def delete_document_type(
    document_type_id: PydanticObjectId = Path(..., title="The ID of the document type to delete")
):
    '''Delete single document type'''
    count = DocumentTypeModel.objects(id=document_type_id).delete()
    if count != 0:
        return JSONResponse(status_code=200, content={"message": DocumentTypeDeletionResponse().message})
    else:
        raise HTTPException(404, {"message": DocumentTypeNotFoundResponse().message})
