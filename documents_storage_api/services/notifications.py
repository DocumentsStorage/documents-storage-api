from models.account.base import AccountModel, NotificationModel
from bson.objectid import ObjectId
from datetime import datetime, timezone

def add_notification(account_id_to_notify, text):
    account_id_to_notify = ObjectId(account_id_to_notify)
    current_date = datetime.now(timezone.utc)
    AccountModel.objects(_id=account_id_to_notify).update_one(add_to_set__notifications=NotificationModel(text=text, creation_date=current_date))
