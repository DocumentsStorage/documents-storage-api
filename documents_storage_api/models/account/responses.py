from pydantic import BaseModel
from common.responses import Message


class AccountNotFoundResponse(Message):
    message = "Not found account"


class WrongCredentialsResponse(Message):
    message = "Check passed username or password"


class AccountUpdatedResponse(Message):
    message = "Account successfully updated"


class AccountDeletionResponse(Message):
    message = "Account successfully deleted"
