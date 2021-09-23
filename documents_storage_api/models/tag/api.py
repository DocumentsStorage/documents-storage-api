from models.tag.base import TagModelAPI

# Input Models


_create_fields = TagModelAPI.__fields__.keys() - {'name'}


class CreateTagModel(TagModelAPI, optional_fields=_create_fields):
    class Config:
        schema_extra = {
            "example": {
                "name": "Invoice"
            }
        }


_update_fields = TagModelAPI.__fields__.keys() - {'name'}


class UpdateTagModel(TagModelAPI, optional_fields=_update_fields):
    class Config:
        schema_extra = {
            "example": {
                "name": "Invoice"
            }
        }
