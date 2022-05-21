from distutils.util import strtobool
import json
from models.account.base import AccountModel
from models.document_type.base import DocumentTypeModel
from services.hash_password import hash_password
import random
import string
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def create_admin_account():
    '''Create basic admin account'''
    found_objects = list(AccountModel.objects(
        **{"rank": "admin"}))
    if len(found_objects) == 0:
        testing = (getenv('TEST', 'False') == 'True')
        generated_password = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=15))
        admin_password = "test_password" if testing else generated_password
        hashed_password = hash_password(admin_password)
        account = AccountModel(
            new_account=True,
            username="admin",
            password=hashed_password,
            rank="admin")
        account.save()
        print("---------------------------")
        print("Running test env: ", testing)
        print("---------------------------")
        print("Generating admin account")
        print("user: admin")
        
        print(f"password: {admin_password}")
        print("Please, change admin password to something else")
        print("because anyone who will have access to this log will be able to login with admin account.")
        print("Thanks! :)")
        print("---------------------------")


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
        print("---------------------------")
