from json import loads
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from middlewares.require_auth import UserChecker, PermissionsChecker, UserCheckerModel
from models.account import AccountModel, AccountModelAPI
from services.hash_password import hash_password, verify_password

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}}
)


@router.get("/session")
async def current_account(user: UserCheckerModel = Depends(UserChecker)):
    '''Get current session account data'''
    try:
        account = loads(AccountModel.objects(id=user['client_id'])[0].to_json())
        del account["_id"]
        del account["password"]
    except BaseException:
        raise HTTPException(404, "Not found account")
    return account


@router.get("/list")
async def list_accounts(skip: int = 0, limit: int = 10, user: UserCheckerModel = Depends(UserChecker)):
    '''Get list of accounts, requires admin rank'''
    if PermissionsChecker("admin", user['rank']):
        accounts_list = loads(
            AccountModel.objects()[
                skip:skip + limit].to_json())
        for dict in accounts_list:
            del dict["password"]
        return accounts_list


@router.post("/add")
async def add_account(account: AccountModelAPI, user: UserCheckerModel = Depends(UserChecker)):
    '''Add single account'''
    if PermissionsChecker("admin", user['rank']):
        # Check if username is available
        account_object = AccountModel.objects(username=account.username)
        if not account_object:
            account = AccountModel(
                username=account.username,
                password=account.password,
                rank=str(account.rank.value),
                new_account=True
            )
            account = account.save()
            account_id = loads(account.to_json())["_id"]
            return {"id": account_id}
        else:
            raise HTTPException(403, "Username is already taken")


@router.patch("/update")
async def update_accont(account: AccountModelAPI = None, user: UserCheckerModel = Depends(UserChecker)):
    '''Update single account'''
    if account.id == user['client_id'] or PermissionsChecker(
            "admin", user['rank']):
        account_object = dict(account)

        # Check if username is available
        try:
            usernames = AccountModel.objects(username=account.username)
            if usernames:
                raise HTTPException(403, "Username is already taken")
        except BaseException:
            pass

        # Delete not passed properties
        account_object = {
            key: val for key,
            val in account_object.items() if val is not None}

        # Update rank - only admin
        if 'rank' in account_object and PermissionsChecker(
                "admin", user['rank']):
            account_object.update(rank=account.rank.value)

        # Get previous state of account
        try:
            account_from_db = loads(
                AccountModel.objects(
                    id=account.id)[0].to_json())
        except BaseException:
            raise HTTPException(404, "Not found account")

        # Reset password - only admin
        if 'new_password' in account_object and PermissionsChecker("admin", user['rank']):
            account_object["password"] = hash_password(account_object['new_password'])
        elif 'new_password' in account_object and 'password' in account_object:
            # Update password
            if verify_password(account_from_db['password'], account_object['password']):
                account_object["password"] = hash_password(account_object['new_password'])
            else:
                raise HTTPException(403, "Invalid old password")
        else:
            try:
                del account_object["password"]
                del account_object["new_password"]
            except KeyError:
                pass

        # Update dict which will be uploaded to db
        account_from_db.update(account_object)

        # Save in db
        AccountModel.objects(id=account.id).update(
            username=account_from_db['username'],
            password=account_from_db['password'],
            rank=account_from_db['rank'],
            new_account=False
        )
        return {"updated": True}


@router.delete("/delete")
async def delete_account(account_id: str = "", user: UserCheckerModel = Depends(UserChecker)):
    '''Delete single account'''
    count = AccountModel.objects(id=ObjectId(account_id)).delete()
    if count != 0:
        return {"delete": True}
    else:
        raise HTTPException(404, "Not found account")
