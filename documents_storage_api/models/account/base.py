from mongoengine import Document
from mongoengine.fields import BooleanField, ListField, StringField

from typing import List, Optional
from pydantic import BaseModel, validator

from middlewares.require_auth import RankEnum
from models.common import PydanticObjectId

# API Models


class AccountModelAPI(BaseModel):
    '''Account Base model'''
    id: PydanticObjectId
    username: str
    password: str
    new_password: str
    rank: RankEnum
    notifications: List[str]

    def __init_subclass__(cls, optional_fields=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if optional_fields:
            for field in optional_fields:
                cls.__fields__[field].outer_type_ = Optional
                cls.__fields__[field].required = False

    @validator('username')
    def username_has_to_have_one_char(cls, v):
        if len(v) == 0:
            raise ValueError('must contain at least one char')
        return v

    @validator('new_password')
    def new_password_has_to_have_one_char(cls, v):
        if len(v) == 0:
            raise ValueError('must contain at least one char')
        return v


# Mongoengine Models

class AccountModel(Document):
    '''Account model for mongoengine'''
    meta = {"collection": "accounts"}
    username = StringField()
    password = StringField()
    rank = StringField()
    new_account = BooleanField()
    notifications = ListField(StringField(), 5)
