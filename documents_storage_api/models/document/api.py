from models.document.base import DocumentModelAPI

# Example

example = {
    "example": {
        "title": "Invoice title",
        "description": "Invoice description",
        "fields": [
            {
                "name": "Seller name",
                        "value": "xox"
            },
            {
                "name": "Amount",
                        "value": 4.12
            },
            {
                "name": "Date",
                        "value": "2021-09-14T14:27:24.000+00:00"
            },
        ],
        "media_files": ["b4ca8076f9ad465da64b7a5079a74ed7", "ec2a52c0a3c44f479d5b7bc59996cade"]
    }
}

# Input Models


_create_fields = DocumentModelAPI.__fields__.keys()


class CreateDocumentModel(DocumentModelAPI, optional_fields=_create_fields):
    class Config:
        schema_extra = example


_update_fields = DocumentModelAPI.__fields__.keys()


class UpdateDocumentModel(DocumentModelAPI, optional_fields=_update_fields):
    class Config:
        schema_extra = example
