from common.responses import Message


class DocumentUpdatedResponse(Message):
    message = "Document successfully updated"


class DocumentNotFoundResponse(Message):
    message = "Not found document"


class DocumentDeletionResponse(Message):
    message = "Document successfully deleted"
