
from mongoengine.queryset.visitor import Q as MQ
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


def createTitle(document, fields):
    # Create document title basing on supplied fields or pushed title
    if document.title is None or len(document.title) == 0:
        title = ""
        
        # Search for first text field
        for field in fields:
            if type(field["value"]) is str:
                title = " ".join(field["value"].split()[:3])
                break
        if len(document.description)>0 and len(title)==0:
            title = " ".join(document.description.split()[:3])
        elif len(title) == 0:
            # Get first field as title
            title = str(fields[0]["value"])
    else:
        title = document.title
    return title

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

    title = createTitle(document, fields)
    
    document_object = DocumentModel(
        ngrams=createNgrams(document),
        creation_date=datetime.now(),
        title=title,
        description=document.description,
        tags=document.tags,
        media_files=media_files,
        fields=fields
    )
    document = document_object.save()
    document_id = loads(document.to_json())["_id"]
    return JSONResponse(status_code=201, content={"id": document_id, "title": title})


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
        
    document_object["title"] = createTitle(document, fields)

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
    return {"message": DocumentUpdatedResponse().message, "title": document_object["title"]}


@router.get("",
            responses={200: {"description": "Successfully obtains list of documents"}})
async def get_documents_list(
    skip: int = 0,
    limit: int = 30
):
    '''Get list of documents'''
    document_objects = DocumentModel.objects().only(*return_only_fields)
    documents_parsed = loads(document_objects[skip:skip + limit].to_json())
    return JSONResponse(status_code=200, content={"total": document_objects.count(), "documents": documents_parsed})


@router.get("/search",
            responses={200: {"description": "Returns found documents"}, 404: {"model": DocumentNotFoundResponse}})
async def search_documents_by_text(
    skip: int = 0,
    limit: int = 30,
    search_text: List[str] = Query(None)
):
    '''
    Search documents by text, words with length higher or equal to 3 will be searched with ngrams,
    other words (with length < 3) will be searched by regex (slower)
    '''
    ngrams, other_words = [], ['']
    for word in search_text:
        ngrams.append(word) if len(word) > 2 else other_words.append(word)
    last_word = other_words[len(other_words)-1].lower()
    ngrams = list(map(lambda x: x.lower(), ngrams))

    if len(ngrams) > 0:
        query = (MQ(ngrams__in=ngrams))
    else:
        query = (MQ(ngrams__contains=last_word))

    document_objects = DocumentModel.objects(query).only(*return_only_fields)
    total = len(document_objects)
    documents_parsed = loads(document_objects[skip:skip + limit].to_json())
    if total > 0:
        return JSONResponse(status_code=200, content={"total": total, "documents": documents_parsed})
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
