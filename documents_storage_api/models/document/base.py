import datetime
from bson.objectid import ObjectId
from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (
    ObjectIdField,
    DateTimeField,
    DynamicField,
    EmbeddedDocumentListField,
    ListField,
    ReferenceField,
    StringField,
    UUIDField
)
from typing import Optional, List, Union
from mongoengine.queryset.base import PULL
from pydantic import BaseModel

from models.common import PydanticObjectId, PydanticUUIDString
from models.tag.base import TagModel


class DocumentFieldModelAPI(BaseModel):
    '''DocumentField for API'''
    name: Optional[str]
    value: Optional[Union[float, int, datetime.datetime, str]]


# API Models

class DocumentModelAPI(BaseModel):
    '''DocumentType Base model'''
    _id: PydanticObjectId
    title: str
    description: str
    tags: List[PydanticObjectId]
    media_files: List[PydanticUUIDString]
    fields: List[DocumentFieldModelAPI]

    def __init_subclass__(cls, optional_fields=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if optional_fields:
            for field in optional_fields:
                cls.__fields__[field].outer_type_ = Optional
                cls.__fields__[field].required = False


# Mongoengine Models


class DocumentFieldModel(EmbeddedDocument):
    '''DocumentField for mongoengine'''
    name = StringField()
    value = DynamicField()


class DocumentModel(Document):
    '''Document model for mongoengine'''
    meta = {"collection": "documents"}
    _id = ObjectIdField(primary_key=True)
    creation_date = DateTimeField()
    modification_date = DateTimeField()
    ngrams = ListField(StringField())
    title = StringField()
    description = StringField()
    tags = ListField(ReferenceField(TagModel, reverse_delete_rule=PULL))
    media_files = ListField(UUIDField())
    fields = EmbeddedDocumentListField(DocumentFieldModel)