import datetime
from enum import unique
from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DynamicField, EmbeddedDocumentListField, ListField, StringField
from typing import Optional, List, Union
from pydantic import BaseModel

# Models


class DocumentFieldModelAPI(BaseModel):
    '''DocumentField for API'''
    name: Optional[str]
    value: Optional[Union[int, datetime.datetime, str]]


class DocumentModelAPI(BaseModel):
    '''Account model for API'''
    id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    media_files: Optional[List[str]]
    fields: Optional[List[DocumentFieldModelAPI]]

    class Config:
        schema_extra = {
            "example": {
                "title": "Invoice title",
                "description": "Invoice description",
                "fields": [
                    {
                        "name": "Seller name",
                        "value": "xox"
                    },
                ],
                "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
            }
        }


class DocumentFieldModel(EmbeddedDocument):
    '''DocumentField for mongoengine'''
    name = StringField(unique=True)
    value = DynamicField()


class DocumentModel(Document):
    '''Document model for mongoengine'''
    meta = {"collection": "documents"}
    title = StringField()
    description = StringField()
    media_files = ListField(StringField())
    fields = EmbeddedDocumentListField(DocumentFieldModel)
