from common.responses import Message


class DocumentTypeTitleTakenResponse(Message):
    message = "Document type title is already taken"


class DocumentTypeUpdatedResponse(Message):
    message = "Document type successfully updated"


class DocumentTypeNotFoundResponse(Message):
    message = "Not found document type"


class DocumentTypeDeletionResponse(Message):
    message = "Document type successfully deleted"
