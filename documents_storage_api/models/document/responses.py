from common.responses import Message


class DocumentUpdatedResponse(Message):
    message = "Document successfully updated"
    title = str


class DocumentNotFoundResponse(Message):
    message = "Not found document"


class DocumentDeletionResponse(Message):
    message = "Document successfully deleted"
