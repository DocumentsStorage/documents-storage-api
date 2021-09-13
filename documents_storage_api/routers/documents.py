from json import loads
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from middlewares.require_auth import UserChecker
from models.document import DocumentFieldModel, DocumentModel, DocumentModelAPI

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(UserChecker)],
    responses={404: {"description": "Not found"}}
)

# Documents


@router.post("")
async def add_document(document: DocumentModelAPI = None):
    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value": field.value_type.value
        })
    document_object = DocumentFieldModel(
        title=document.title,
        description=document.description,
        mediaFiles=document.mediaFiles,
        fields=fields
    )
    document = document_object.save()
    document_id = loads(document.to_json())["_id"]
    return {"id": document_id}


@router.patch("")
async def update_document(document: DocumentModelAPI = None):
    # Delete not passed properties
    document = {
        key: val for key,
        val in document.items() if val is not None}

    fields = []
    for field in document.fields:
        fields.append({
            "name": field.name,
            "value": field.value_type.value
        })
    DocumentModel.objects(id=document.id).update(
        title=document.title,
        description=document.description,
        mediaFiles=document.mediaFiles,
        fields=fields
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
    count = DocumentModel.objects(id=ObjectId(document_id)).delete()
    if count != 0:
        return {"delete": True}
    else:
        raise HTTPException(404, "Not found document")
