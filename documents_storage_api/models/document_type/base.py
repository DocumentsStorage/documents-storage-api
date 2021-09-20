from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentListField, EnumField, StringField

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, validator

from models.common import PydanticObjectId


class ValueTypeEnum(Enum):
    text = "text"
    number = "number"
    date = "date"


# API Models

class DocumentTypeFieldModelAPI(BaseModel):
    '''DocumentTypeField for API'''
    name: str
    value_type: ValueTypeEnum


class DocumentTypeModelAPI(BaseModel):
    '''DocumentType Base model'''
    id: PydanticObjectId
    title: str
    description: str
    fields: List[DocumentTypeFieldModelAPI]

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
        return v


# Mongoengine Models


class DocumentTypeFieldModel(EmbeddedDocument):
    '''DocumentTypeField model for mongoengine'''
    name = StringField()
    value_type = EnumField(ValueTypeEnum)


class DocumentTypeModel(Document):
    '''DocumentType model for mongoengine'''
    meta = {"collection": "document_types"}
    title = StringField(unique=True)
    description = StringField()
    fields = EmbeddedDocumentListField(DocumentTypeFieldModel)
