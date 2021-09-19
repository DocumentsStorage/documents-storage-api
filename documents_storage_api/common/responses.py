from pydantic import BaseModel


class Message(BaseModel):
    message: str


class NotEnoughPermissions(Message):
    message = "Not enough permissions"
