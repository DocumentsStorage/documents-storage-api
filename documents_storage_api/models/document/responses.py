from typing import List
from pydantic.fields import Field
from pydantic.main import BaseModel
from common.responses import Message
from models.document.base import DocumentModelAPI


class DocumentsSearchResponse(BaseModel):
    total: int = Field(description="total number of matching documents")
    documents: List[DocumentModelAPI] = Field(description="list of matching documents")
    defined_fields: dict = Field(
        description="""
        Sorted list of user defined field names by their number of occurencies
         (only if greater than 1, otherway it is not included in list)
        """
    )


class DocumentUpdatedResponse(Message):
    message = "Document successfully updated"
    title = str


class DocumentNotFoundResponse(Message):
    message = "Not found document"


class DocumentDeletionResponse(Message):
    message = "Document successfully deleted"
