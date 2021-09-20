from common.responses import Message


class MediaNotFoundResponse(Message):
    message = "Not found media file"


class MediaDeletionResponse(Message):
    message = "Media file successfully deleted"
