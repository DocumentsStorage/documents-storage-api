import json
from models.account.base import AccountModel
from models.document_type.base import DocumentTypeModel
from services.hash_password import hash_password


def create_admin_account():
    '''Create basic admin account'''
    found_objects = list(AccountModel.objects(
        **{"rank": "admin"}))
    if len(found_objects) == 0:
        print("Generating admin account")
        account = AccountModel(
            new_account=True,
            username="admin",
            password=hash_password("documents-storage-supervisor"),
            rank="admin")
        account.save()


def create_predefined_document_types():
    '''Create predefined document types'''
    found_objects = list(DocumentTypeModel.objects())
    if len(found_objects) == 0:
        print("Adding predefined document types")
        with open("predefined_document_types.json", "r") as read_file:
            print("Starting to convert json decoding")
            document_types = json.load(read_file)
        for document_type in document_types:
            fields = []
            for field in document_type['fields']:
                fields.append({
                    "name": field['name'],
                    "value_type": field['value_type']
                })
            document_type = DocumentTypeModel(
                title=document_type['title'],
                description=document_type['description'],
                fields=fields
            )
            document_type.save()
