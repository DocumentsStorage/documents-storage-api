from json import loads
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette.responses import JSONResponse
from common.responses import Message, NotEnoughPermissions
from middlewares.require_auth import UserChecker, PermissionsChecker, UserCheckerModel
from models.account.api import CreateAccountModel, UpdateAccountModel
from models.account.base import AccountModel
from models.account.responses import AccountDeletionResponse, AccountNotFoundResponse, AccountUpdatedResponse
from models.common import PydanticObjectId
from services.hash_password import hash_password, verify_password

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)


@router.get("/session",
            responses={200: {"description": "Successfully obtains current account data"},
                       404: {"model": AccountNotFoundResponse}})
async def get_current_account(
    user: UserCheckerModel = Depends(UserChecker)
):
    '''Get current session account data'''
    account = loads(AccountModel.objects.get(_id=ObjectId(user['client_id'])).to_json())
    del account["_id"]
    del account["password"]
    return account


@router.get("/session/notifications",
            responses={200: {"description": "Successfully obtains notifications from session account"},
                       404: {"model": AccountNotFoundResponse}})
async def get_current_account(
    skip: int = 0,
    limit: int = 5,
    user: UserCheckerModel = Depends(UserChecker)
):
    '''Get notifications from session account'''
    account = loads(AccountModel.objects.get(_id=ObjectId(user['client_id'])).to_json())
    notifications = sorted(account["notifications"], key=lambda d: d['creation_date']['$date'], reverse=True) 
    AccountModel.objects(_id=ObjectId(user['client_id'])).update(**{'set__notifications__$[]__seen':True})
    return JSONResponse({"notifications": notifications[skip:skip + limit]}, 200)


@router.get("/list",
            responses={200: {"description": "Successfully obtains list of accounts"}})
async def get_accounts_list(
    skip: int = 0,
    limit: int = 10,
    user: UserCheckerModel = Depends(UserChecker)
):
    '''Get list of accounts, requires admin rank'''
    if PermissionsChecker("admin", user['rank']):
        accounts_list = loads(
            AccountModel.objects()[
                skip:skip + limit].to_json())
        for dict in accounts_list:
            del dict["password"]
        return accounts_list


@router.post("",
             responses={
                 201: {"description": "Successfully created account"},
                 403: {"model": Message}}
             )
async def add_account(
    account: CreateAccountModel,
    user: UserCheckerModel = Depends(UserChecker)
):
    '''Add single account - requires admin rank'''
    if PermissionsChecker("admin", user['rank']):
        # Check if username is available
        account_object = AccountModel.objects(username=account.username)
        new_id = ObjectId()
        if not account_object:
            password = hash_password(account.new_password)
            account = AccountModel(
                _id=new_id,
                username=account.username,
                password=password,
                rank=str(account.rank.value),
                new_account=True
            ).save()
            account_id = loads(account.to_json())["_id"]
            return JSONResponse(status_code=201, content={"id": account_id})
        else:
            raise HTTPException(403, {"message": "Username is already taken"})
    raise HTTPException(403, {"message": NotEnoughPermissions().message})


@router.patch("/{account_id}",
              response_model=Message,
              responses={200: {"model": AccountUpdatedResponse},
                         403: {"model": Message},
                         404: {"model": AccountNotFoundResponse}})
async def update_accont(
        account: UpdateAccountModel,
        user: UserCheckerModel = Depends(UserChecker),
        account_id: PydanticObjectId = Path(..., title="The ID of the account to update")
):
    '''Account can be updated by owner or user with admin rank'''
    if str(account_id) == user['client_id'] or PermissionsChecker("admin", user['rank']):
        account_object = dict(account)

        # Check if username is available
        usernames = AccountModel.objects(username=account.username)
        if usernames:
            raise HTTPException(403, {"message": "Username is already taken"})

        # Delete not passed properties
        account_object = {
            key: val for key,
            val in account_object.items() if val is not None}

        # Update rank - only admin
        if 'rank' in account_object and PermissionsChecker("admin", user['rank']):
            account_object.update(rank=account.rank.value)

        # Get previous state of account
        try:
            account_from_db = loads(
                AccountModel.objects(_id=account_id)[0].to_json())
        except BaseException:
            raise HTTPException(404, {"message": AccountNotFoundResponse().message})

        # Reset password - only admin
        if 'new_password' in account_object and PermissionsChecker("admin", user['rank'], False):
            # Check if admin is changing password for himself
            if str(account_id) == user['client_id']:
                if verify_password(account_from_db['password'], account_object['password']):
                    account_object["password"] = hash_password(account_object['new_password'])
                else:
                    raise HTTPException(403, {"message": """While updating password for user with admin rank,
                                              pass valid old password"""})
            else:
                account_object["password"] = hash_password(account_object['new_password'])
        elif 'new_password' in account_object and 'password' in account_object:
            # Update password
            if verify_password(account_from_db['password'], account_object['password']):
                account_object["password"] = hash_password(account_object['new_password'])
            else:
                raise HTTPException(403, {"message": "Invalid old password"})
        else:
            try:
                del account_object["password"]
                del account_object["new_password"]
            except KeyError:
                pass

        # Update dict which will be uploaded to db
        account_from_db.update(account_object)

        # Save in db
        AccountModel.objects(_id=account_id).update(
            username=account_from_db['username'],
            password=account_from_db['password'],
            rank=account_from_db['rank'],
            new_account=False
        )
        return {"message": AccountUpdatedResponse().message}
    raise HTTPException(403, {"message": NotEnoughPermissions().message})


@router.delete("/{account_id}",
               responses={200: {"model": AccountDeletionResponse}, 404: {"model": AccountNotFoundResponse}})
async def delete_account(
    account_id: PydanticObjectId = Path(..., title="The ID of the account to delete"),
    user: UserCheckerModel = Depends(UserChecker)
):
    '''Delete single account'''
    if account_id == user['client_id'] or PermissionsChecker("admin", user['rank']):
        count = AccountModel.objects(_id=account_id).delete()
        if count != 0:
            return {"message": AccountDeletionResponse().message}
        else:
            raise HTTPException(404, {"message": AccountNotFoundResponse().message})
    else:
        raise HTTPException(403, {"message": NotEnoughPermissions().message})
