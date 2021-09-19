from models.account.base import AccountModelAPI

# Input Models


_create_fields = AccountModelAPI.__fields__.keys() - {'username', 'new_password', 'rank'}


class CreateAccountModel(AccountModelAPI, optional_fields=_create_fields):
    class Config:
        schema_extra = {
            "example": {
                "username": "John",
                "new_password": "36smA4Sd",
                "rank": "user"
            }
        }


_update_fields = AccountModelAPI.__fields__.keys()


class UpdateAccountModel(AccountModelAPI, optional_fields=_update_fields):
    class Config:
        schema_extra = {
            "example": {
                "username": "new_username",
                "password": "old_password",
                "new_password": "new_password",
                "rank": "user"
            }
        }
