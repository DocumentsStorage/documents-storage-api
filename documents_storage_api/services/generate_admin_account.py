from models.account.base import AccountModelDB
from services.hash_password import hash_password


def create_admin_account():
    '''Create basic admin account'''
    found_objects = list(AccountModelDB.objects(
        **{"rank": "admin"}))
    if len(found_objects) == 0:
        print("Generating admin account")
        account = AccountModelDB(
            new_account=True,
            username="admin",
            password=hash_password("documents-storage-supervisor"),
            rank="admin")
        account.save()
