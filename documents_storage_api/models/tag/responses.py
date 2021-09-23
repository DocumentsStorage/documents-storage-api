from common.responses import Message


class TagNameTakenResponse(Message):
    message = "Tag name is already taken"


class TagUpdatedResponse(Message):
    message = "Tag successfully updated"


class SomeTagsNotFoundResponse(Message):
    message = "Some tags were not found"


class NoTagsFoundResponse(Message):
    message = "No tags were found"


class TagDeletionResponse(Message):
    message = "Tag successfully deleted"
