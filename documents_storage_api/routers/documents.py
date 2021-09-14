from json import loads
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from mongoengine.fields import StringField
from middlewares.require_auth import UserChecker
from models.document import DocumentFieldModel, DocumentModel, DocumentModelAPI

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    # dependencies=[Depends(UserChecker)],
    responses={404: {"description": "Not found"}}
)

# Documents


@router.post("")
async def add_document(document: DocumentModelAPI):
    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value": field.value
        })
    document_object = DocumentModel(
        title=document.title,
        description=document.description,
        media_files=document.media_files,
        fields=fields
    )
    document = document_object.save()
    document_id = loads(document.to_json())["_id"]
    return {"id": document_id}


@router.patch("")
async def update_document(document: DocumentModelAPI = None):
    document_object = dict(document)

    # Delete not passed properties
    document_object = {
        key: val for key,
        val in document_object.items() if val is not None}

    # Get previous state of account
    try:
        document_from_db = loads(
            DocumentModel.objects(
                id=document.id)[0].to_json())
    except BaseException:
        raise HTTPException(404, "Not found document")

    # Update dict which will be uploaded to db
    document_from_db.update(document_object)

    DocumentModel.objects(id=document.id).update(
        title=document_from_db['title'],
        description=document_from_db['description'],
        media_files=document_from_db['media_files']
    )

    # TODO: Update fields

    return {"updated": True}


@router.get("")
async def get_documents_list(skip: int = 0, limit: int = 30):
    '''Get list of documents'''
    documents_list = loads(
        DocumentModel.objects()[skip:skip + limit].to_json())
    return documents_list


@router.delete("")
async def delete_document(document_id: str = ""):
    '''Delete single document'''
    count = DocumentModel.objects(id=ObjectId(document_id)).delete()
    if count != 0:
        return {"delete": True}
    else:
        raise HTTPException(404, "Not found document")