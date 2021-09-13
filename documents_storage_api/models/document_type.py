from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentListField, EnumField, StringField

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

# Models


class ValueTypeEnum(Enum):
    text = "text"
    number = "number"
    date = "date"


class DocumentTypeFieldModelAPI(BaseModel):
    '''DocumentTypeField for API'''
    name: Optional[str]
    value_type: Optional[ValueTypeEnum]


class DocumentTypeModelAPI(BaseModel):
    '''Account model for API'''
    id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    fields: Optional[List[DocumentTypeFieldModelAPI]]

    class Config:
        schema_extra = {
            "example": {
                "title": "Invoice",
                "description": "Invoice document",
                "fields": [
                    {
                        "name": "Seller name",
                        "value_type": "text"
                    },
                    {
                        "name": "Buyer name",
                        "value_type": "text"
                    },
                    {
                        "name": "Date",
                        "value_type": "date"
                    },
                    {
                        "name": "Total amount",
                        "value_type": "number"
                    },
                    {
                        "name": "Amount currency",
                        "value_type": "text"
                    }
                ]
            }
        }


class DocumentTypeFieldModel(EmbeddedDocument):
    '''DocumentTypeField for mongoengine'''
    name = StringField()
    value_type = EnumField(ValueTypeEnum)


class DocumentTypeModel(Document):
    '''DocumentType model for mongoengine'''
    meta = {"collection": "documents_types"}
    title = StringField()
    description = StringField()
    fields = EmbeddedDocumentListField(DocumentTypeFieldModel)
