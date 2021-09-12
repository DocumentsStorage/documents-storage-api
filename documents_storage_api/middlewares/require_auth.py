from fastapi import Depends, HTTPException
from enum import Enum
from fastapi.security import OAuth2PasswordBearer
from pydantic.main import BaseModel
from services.auth import jwt_authorize

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ranks = ["admin", "user"]


class RankEnum(Enum):
    admin = "admin"
    user = "user"


class UserCheckerModel(BaseModel):
    id: str
    rank: RankEnum


async def UserChecker(token: str = Depends(oauth2_scheme)):
    '''Get rank name for passed JWT token'''
    decoded_token = jwt_authorize(token)
    if not decoded_token:
        raise HTTPException(401, "Incorrect access_token provided")
    return decoded_token


def PermissionsChecker(required_rank: RankEnum, user_rank: RankEnum):
    '''Check if given user_rank is higher in hierarchy than required_rank'''
    user_rank_index = RankEnum[required_rank]
    user_rank_index = ranks.index(user_rank)
    if user_rank_index <= ranks.index(required_rank):
        return True
    else:
        raise HTTPException(403, "Not enough permission")
