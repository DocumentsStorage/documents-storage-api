from json import loads
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from middlewares.require_auth import UserChecker, UserCheckerModel
from models.document_type import DocumentTypeModel, DocumentTypeModelAPI

router = APIRouter(
    prefix="/document_types",
    tags=["document_types"],
    dependencies=[Depends(UserChecker)],
    responses={404: {"description": "Not found"}}
)


@router.post("")
async def add_document_type(document_type: DocumentTypeModelAPI):
    '''Add single document type'''
    fields = []
    for field in document_type.fields:
        fields.append({
            "name": field.name,
            "value_type": field.value_type.value
        })
    document_type_object = DocumentTypeModel(
        title=document_type.title,
        description=document_type.description,
        fields=fields,
        media_files=document_type.media_files
    )
    document_type = document_type_object.save()
    document_type_id = loads(document_type.to_json())["_id"]
    return {"id": document_type_id}


@router.get("")
async def get_document_types_list(skip: int = 0, limit: int = 10):
    '''Get list of document types'''
    document_types_list = loads(
        DocumentTypeModel.objects()[skip:skip + limit].to_json())
    return document_types_list


@router.delete("")
async def delete_document_type(document_type_id: str = ""):
    '''Delete single document type'''
    count = DocumentTypeModel.objects(id=ObjectId(document_type_id)).delete()
    if count != 0:
        return {"delete": True}
    else:
        raise HTTPException(404, "Not found document type")
