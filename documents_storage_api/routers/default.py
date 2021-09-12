from json import loads
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models.account import AccountModel
from services.auth import jwt_authenticate
from services.hash_password import verify_password

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/ping")
def ping():
    return {"Ping": "pong"}


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    accounts_list = AccountModel.objects(username=form_data.username)
    if len(accounts_list) > 0:
        account = loads(accounts_list[0].to_json())
        if verify_password(account['password'], form_data.password):
            return {
                "access_token": jwt_authenticate(
                    account['_id']['$oid'],
                    account['rank']),
                "token_type": "bearer"}
    raise HTTPException(403, "Check passed username or password")
