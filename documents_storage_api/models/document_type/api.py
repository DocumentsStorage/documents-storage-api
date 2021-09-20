from models.document_type.base import DocumentTypeModelAPI

# Input Models


_create_fields = DocumentTypeModelAPI.__fields__.keys() - {'title'}


class CreateDocumentTypeModel(DocumentTypeModelAPI, optional_fields=_create_fields):
    class Config:
        schema_extra = {
            "example": {
                "title": "Invoice",
                "description": "Invoice document",
                "fields": [
                    {
                        "name": "Seller name",
                        "value_type": "text"
                    },
                    {
                        "name": "Buyer name",
                        "value_type": "text"
                    },
                    {
                        "name": "Date",
                        "value_type": "date"
                    },
                    {
                        "name": "Total amount",
                        "value_type": "number"
                    },
                    {
                        "name": "Amount currency",
                        "value_type": "text"
                    }
                ]
            }
        }


_update_fields = DocumentTypeModelAPI.__fields__.keys()


class UpdateDocumentTypeModel(DocumentTypeModelAPI, optional_fields=_update_fields):
    class Config:
        schema_extra = {
            "example": {
                "title": "Invoice",
                "fields": [
                    {
                        "name": "Seller name",
                        "value_type": "text"
                    },
                    {
                        "name": "Buyer name",
                        "value_type": "text"
                    },
                    {
                        "name": "Date",
                        "value_type": "date"
                    },
                    {
                        "name": "Total amount",
                        "value_type": "number"
                    },
                    {
                        "name": "Amount currency",
                        "value_type": "text"
                    }
                ]
            }
        }
