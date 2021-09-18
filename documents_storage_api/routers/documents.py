from datetime import datetime
from json import loads
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from middlewares.require_auth import UserChecker
from models.document import DocumentModel, DocumentModelAPI
from routers.media import delete_media_files

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(UserChecker)],
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
        creation_date=datetime.now(),
        title=document.title,
        description=document.description,
        media_files=document.media_files,
        fields=fields
    )
    document = document_object.save()
    document_id = loads(document.to_json())["_id"]
    return {"id": document_id}


@router.put("")
async def update_document(document: DocumentModelAPI = None):
    '''This path allow to - update: title, description and overwrite: fields, media_files'''
    document_object = dict(document)

    # Delete not passed properties
    document_object = {
        key: val for key,
        val in document_object.items() if val is not None}

    # Get previous state of document
    try:
        document_from_db = loads(
            DocumentModel.objects(
                id=document.id)[0].to_json())
    except BaseException:
        raise HTTPException(404, "Not found document")

    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value": field.value
        })

    media_files = document.media_files
    # Update dict which will be uploaded to db
    document_from_db.update(document_object)

    DocumentModel.objects(id=document.id).update(
        modification_date=datetime.now(),
        title=document_from_db['title'],
        description=document_from_db['description'],
        media_files=media_files,
        set__fields=fields
    )

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
    document_object = DocumentModel.objects(id=ObjectId(document_id))
    document_json = loads(document_object.to_json())[0]
    await delete_media_files(document_json['media_files'])
    count = document_object.delete()
    if count != 0:
        return {"delete": True}
    else:
        raise HTTPException(404, "Not found document")
