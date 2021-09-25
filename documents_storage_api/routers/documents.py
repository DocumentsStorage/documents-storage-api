from datetime import datetime
from json import loads
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path, Query
from starlette.responses import JSONResponse
from middlewares.require_auth import UserChecker
from models.common import PydanticObjectId, UUIDFromString
from models.document.api import CreateDocumentModel, UpdateDocumentModel
from models.document.base import DocumentModel, DocumentModelAPI
from models.document.responses import DocumentDeletionResponse, DocumentNotFoundResponse, DocumentUpdatedResponse
from routers.media import delete_media_files
from services.ngram import create_ngram

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(UserChecker)],
)


return_only_fields = list(map(lambda key: key, DocumentModelAPI.__fields__.keys()))


def StringFromUUID(media_files):
    return list(map(lambda file: str(file['$uuid']), media_files))


def createNgrams(all_fields: UpdateDocumentModel):
    ngrams = []
    if all_fields.title:
        ngrams += create_ngram(all_fields.title)
    if all_fields.description:
        ngrams += create_ngram(all_fields.description)
    if all_fields.fields:
        for field in all_fields.fields:
            ngrams += create_ngram(field.name)
            if isinstance(field.value, str):
                ngrams += create_ngram(field.value)
    # Remove duplicates
    ngrams = list(set(ngrams))
    return ngrams


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
        ngrams=createNgrams(document),
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
        ngrams=createNgrams(document),
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
        DocumentModel.objects().only(*return_only_fields)[skip:skip + limit].to_json())
    return documents_list


@router.get("/",
            responses={200: {"description": "Returns found documents"}, 404: {"model": DocumentNotFoundResponse}})
async def search_documents_by_text(
    skip: int = 0,
    limit: int = 30,
    search_text: List[str] = Query(None)
):
    '''Search documents by text, only words with length higher or equal to 3 will be searched for'''
    search_text = filter(lambda x: len(x) > 2, search_text)
    document_objects = loads(DocumentModel.objects(ngrams__in=search_text)
                             .only(*return_only_fields)[skip:skip + limit].to_json())
    if len(document_objects) > 0:
        return JSONResponse(status_code=200, content={"documents": document_objects})
    else:
        raise HTTPException(404, {"message": DocumentNotFoundResponse().message})


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
