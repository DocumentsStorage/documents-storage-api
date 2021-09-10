from mongoengine import Document
from mongoengine.fields import BooleanField, StringField

from typing import Optional
from pydantic import BaseModel

from middlewares.require_auth import RankEnum

# Models


class AccountModelAPI(BaseModel):
    '''Account model for API'''
    id: Optional[str]
    username: Optional[str]
    password: Optional[str]
    new_password: Optional[str]
    rank: Optional[RankEnum]


class AccountModel(Document):
    '''Account model for mongoengine'''
    meta = {"collection": "accounts"}
    username = StringField()
    password = StringField()
    rank = StringField()
    new_account = BooleanField()