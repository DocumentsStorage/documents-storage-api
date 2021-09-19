from json import loads
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from models.account.base import AccountModelDB
from models.default.responses import CredentialsResponse, PingResponse, WrongCredentialsResponse
from services.auth import jwt_authenticate
from services.hash_password import verify_password

router = APIRouter()


@router.get("/ping", response_model=PingResponse)
def ping():
    return JSONResponse(status_code=200, content={"message": PingResponse().message})


@router.post("/token",
             responses={
                 200: {"description": "Gained access", "model": CredentialsResponse},
                 403: {"description": "Account not found or given wrong credentials.",
                       "model": WrongCredentialsResponse}
             })
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    accounts_list = AccountModelDB.objects(username=form_data.username)
    if len(accounts_list) > 0:
        account = loads(accounts_list[0].to_json())
        if verify_password(account['password'], form_data.password):
            return {
                "access_token": jwt_authenticate(
                    account['_id']['$oid'],
                    account['rank']),
                "token_type": "bearer"}
    raise HTTPException(403, {"message": WrongCredentialsResponse().message})
