from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.permission import permission_operations

from app.models.user import User

from app.crud.user import user_CRUD_operations
from app.crud.card import Card_CRUD
from app.crud.transaction import transaction_crud

router = APIRouter()

import enum

class Roles(enum.Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


@router.post("/Users/Give_role")
async def give_role(current_user: Annotated[User, Depends(permission_operations.require_permission("users", "manage_role"))],
                    user_id : Annotated[int, Query()],
                    role : Roles):
    user = await user_CRUD_operations.get_user_by_id(user_id)
    if user:
        if await user_CRUD_operations.change_users_role(user_id, role.value):
            return {"message": f"This user is {role.value} now"}
        else:
            return {"message": "Something went wrong with changing this user role"}
    else:
        raise HTTPException(status_code=404, detail="There is no user with this id")

@router.post("/Users/Disable_by_id")
async def change_users_activity(current_user: Annotated[User, Depends(permission_operations.require_permission("users", "delete_any"))],
                            user_id : Annotated[int, Query()]):
    user = await user_CRUD_operations.get_user_by_id(user_id)
    if user:
        if await user_CRUD_operations.change_users_activity(user_id):
            return {"message": "This user is disabled"}
        else:
            return {"message": "Something went wrong with disabling this user"}
    else:
        raise HTTPException(status_code=404, detail="There is no user with this id")

@router.delete("/Users/Delete_by_id")
async def delete_user_by_id(current_user: Annotated[User, Depends(permission_operations.require_permission("users", "delete_any"))],
                            user_id : Annotated[int, Query()]):
    user = await user_CRUD_operations.get_user_by_id(user_id)
    if user:
        if await user_CRUD_operations.delete_user_by_id(user_id):
            return {"message": "This user is deleted"}
        else:
            return {"message": "Something went wrong with deleting this user"}
    else:
        raise HTTPException(status_code=404, detail="There is no user with this id")


@router.post("/Cards/unfreeze_any")
async def unfreeze_card_by_id(current_user: Annotated[User, Depends(permission_operations.require_permission("cards", "unfreeze_my"))],
                            card_id : int,
                            new_expires_date:date):
    card = await Card_CRUD.get_card_by_id(card_id, -1)
    if card:
        if await Card_CRUD.change_card_expires_date(card_id, -1, new_expires_date):
            return {"message" : "This card is active now"}
        else:
            return {"message" : "Something went wrong with changing cards expires date"}
    else:
        raise HTTPException(status_code=404, detail="There is no card with this id")



@router.delete("/Cards/Delete_by_id")
async def delete_card_by_id(current_user: Annotated[User, Depends(permission_operations.require_permission("cards", "delete_any"))],
                            card_id : Annotated[int, Query()]):
    user = await Card_CRUD.get_card_by_id(card_id, -1)
    if user:
        if await Card_CRUD.delete_card_by_id(card_id, -1):
            return {"message": "This card is deleted"}
        else:
            return {"message": "Something went wrong with deleting this card"}
    else:
        raise HTTPException(status_code=404, detail="There is no card with this id")

@router.delete("/Transactions/Delete_by_id")
async def delete_transaction_by_id(current_user: Annotated[User, Depends(permission_operations.require_permission("transactions", "delete_any"))],
                                   transaction_id : Annotated[int, Query()]):
    transaction = await transaction_crud.get_transaction_by_id(transaction_id)
    if transaction:
        result = await transaction_crud.delete_transaction_by_id(transaction_id)
        if result:
            return {"message":"This transaction was successfully deleted"}
        else:
            return {"message" : "Something went wrong with deleting this transaction"}
    else:
        raise HTTPException(status_code=404, detail="There is no transaction with this id")

