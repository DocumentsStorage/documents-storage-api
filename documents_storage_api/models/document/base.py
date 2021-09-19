import datetime
from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DateTimeField, DynamicField, EmbeddedDocumentListField, ListField, StringField
from typing import Optional, List, Union
from pydantic import BaseModel

from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentListField, StringField

from typing import Optional, List
from pydantic import BaseModel, validator

from models.common import PydanticObjectId


class DocumentFieldModelAPI(BaseModel):
    '''DocumentField for API'''
    name: Optional[str]
    value: Optional[Union[float, int, datetime.datetime, str]]


# API Models

class DocumentModelAPI(BaseModel):
    '''DocumentType Base model'''
    id: PydanticObjectId
    title: str
    description: str
    media_files: List[str]
    fields: List[DocumentFieldModelAPI]

    def __init_subclass__(cls, optional_fields=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if optional_fields:
            for field in optional_fields:
                cls.__fields__[field].outer_type_ = Optional
                cls.__fields__[field].required = False

    @validator('title')
    def title_has_to_have_one_char(cls, v):
        if len(v) == 0:
            raise ValueError('must contain at least one char')
        return v.title()


# Mongoengine Models


class DocumentFieldModel(EmbeddedDocument):
    '''DocumentField for mongoengine'''
    name = StringField()
    value = DynamicField()


class DocumentModel(Document):
    '''Document model for mongoengine'''
    meta = {"collection": "documents"}
    creation_date = DateTimeField()
    modification_date = DateTimeField()
    title = StringField(required=True)
    description = StringField()
    media_files = ListField(StringField())
    fields = EmbeddedDocumentListField(DocumentFieldModel)
