from mongoengine import Document
from mongoengine.fields import BooleanField, StringField

from typing import Optional
from pydantic import BaseModel, ValidationError, validator

from middlewares.require_auth import RankEnum

# API Models


class AccountModelAPI(BaseModel):
    '''Account model for API'''
    id: str
    username: str
    password: str
    new_password: Optional[str]
    rank: RankEnum

    def __init_subclass__(cls, optional_fields=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if optional_fields:
            for field in optional_fields:
                print(field)
                cls.__fields__[field].outer_type_ = Optional
                cls.__fields__[field].required = False


# Set required fields
_create_fields = AccountModelAPI.__fields__.keys() - {'username', 'password', 'rank'}


class CreateAccountModel(AccountModelAPI, optional_fields=_create_fields):
    @validator('username')
    def username_has_to_have_one_char(cls, v):
        if len(v) == 0:
            raise ValueError('must contain at least one char')
        return v.title()

    @validator('password')
    def password_has_to_have_one_char(cls, v):
        if len(v) == 0:
            raise ValueError('must contain at least one char')
        return v.title()

    class Config:
        schema_extra = {
            "example": {
                "username": "John",
                "password": "36smA4Sd",
                "rank": "user"
            }
        }


# Set required fields
_update_fields = AccountModelAPI.__fields__.keys() - {'id'}


class UpdateAccountModel(AccountModelAPI, optional_fields=_update_fields):
    class Config:
        schema_extra = {
            "example": {
                "id": ""
            }
        }


# Mongoengine Models

class AccountModelDB(Document):
    '''Account model for mongoengine'''
    meta = {"collection": "accounts"}
    username = StringField()
    password = StringField()
    rank = StringField()
    new_account = BooleanField()
