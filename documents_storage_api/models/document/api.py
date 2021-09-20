from models.document.base import DocumentModelAPI

# Input Models


_create_fields = DocumentModelAPI.__fields__.keys() - {'title'}


class CreateDocumentModel(DocumentModelAPI, optional_fields=_create_fields):
    class Config:
        schema_extra = {
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
                "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
            }
        }


_update_fields = DocumentModelAPI.__fields__.keys()


class UpdateDocumentModel(DocumentModelAPI, optional_fields=_update_fields):
    class Config:
        schema_extra = {
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
                "media_files": ["4156883c-a183-4d59-b87a-44cbc4cc2fba", "55d42121-d533-4c5e-9591-e324aaaf73a3"]
            }
        }
