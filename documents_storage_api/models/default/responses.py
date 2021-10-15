from pydantic import BaseModel
from common.responses import Message


class PingResponse(Message):
    message = "pong"


class CredentialsResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class WrongCredentialsResponse(Message):
    message = "Check passed username or password"


class WrongJWTResponse(Message):
    message = "Check passed JWT token"
