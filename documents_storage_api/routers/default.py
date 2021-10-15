from json import loads
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from models.account.base import AccountModel
from models.default.responses import CredentialsResponse, PingResponse, WrongCredentialsResponse, WrongJWTResponse
from services.auth import jwt_authenticate, jwt_authorize
from services.hash_password import verify_password
from middlewares.require_auth import oauth2_scheme

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
    accounts_list = AccountModel.objects(username=form_data.username)
    if len(accounts_list) > 0:
        account = loads(accounts_list[0].to_json())
        if verify_password(account['password'], form_data.password):
            return {
                "access_token": jwt_authenticate(
                    account['_id']['$oid'],
                    account['rank']),
                "token_type": "bearer"}
    raise HTTPException(403, {"message": WrongCredentialsResponse().message})


@router.post("/token/update",
             responses={
                200: {"description": "Successfully updated token", "model": CredentialsResponse},
                403: {"description": "Given wrong JWT token", "model": WrongJWTResponse}
             })
async def update_token(token: str = Depends(oauth2_scheme)):
    jwt = jwt_authorize(token)
    if jwt:
        return {
            "access_token": jwt_authenticate(
                jwt['client_id'],
                jwt['rank']),
            "token_type": "bearer"}
    raise HTTPException(403, {"message": WrongJWTResponse().message})
