from mongoengine import Document
from mongoengine.fields import StringField

from typing import Optional
from pydantic import BaseModel, validator

from models.common import PydanticObjectId


# API Models


class TagModelAPI(BaseModel):
    '''Tag Base model'''
    id: PydanticObjectId
    name: str

    def __init_subclass__(cls, optional_fields=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if optional_fields:
            for field in optional_fields:
                cls.__fields__[field].outer_type_ = Optional
                cls.__fields__[field].required = False

    @validator('name')
    def tag_name_has_to_have_one_char(cls, v):
        if len(v) == 0:
            raise ValueError('must contain at least one char')
        return v


# Mongoengine Models


class TagModel(Document):
    '''Tag model for mongoengine'''
    meta = {"collection": "tags"}
    name = StringField(unique=True)
