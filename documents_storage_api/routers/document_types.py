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

    document_type_object = DocumentTypeModel.objects(title=document_type.title)
    if not document_type_object:
        document_type = DocumentTypeModel(
            title=document_type.title,
            description=document_type.description,
            fields=fields,
        )
        document_type = document_type.save()
        document_type_id = loads(document_type.to_json())["_id"]
        return {"id": document_type_id}
    else:
        raise HTTPException(403, "Document type title is already taken")


@router.put("")
async def update_document_type(document: DocumentTypeModelAPI = None):
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
                id=document.id)[0].to_json())
    except BaseException:
        raise HTTPException(404, "Not found document type")

    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value_type": field.value_type.value
        })
    # Update dict which will be uploaded to db
    document_from_db.update(document_type_object)

    DocumentTypeModel.objects(id=document.id).update(
        title=document_from_db['title'],
        description=document_from_db['description'],
        set__fields=fields
    )

    return {"updated": True}


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
