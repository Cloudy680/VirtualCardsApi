from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import verify_password
from app.api.permission import permission_operations

from app.services.validate_service import validate_service_obj

from app.models.user import User, User_In_DB, user_operations

from app.crud.user import user_CRUD_operations

router = APIRouter()


@router.get("/Get info", response_model=User)
async def get_my_account_info(current_user: Annotated[User, Depends(permission_operations.require_permission("account", "show_info"))]):
    return current_user

@router.post("/Change info")
async def change_my_account_info(current_user: Annotated[User, Depends(permission_operations.require_permission("account", "change_info"))],
                                 repeat_password: Annotated[str, Query(description = "Password must contain: small letter, capital letter, digit, special symbol", min_length = 6)],
                                 new_username: Annotated[str, Query(max_length=25)] = None,
                                 new_password: Annotated[str, Query(description="Password must contain: small letter, capital letter, digit, special symbol",min_length=6)] = None,
                                 new_email: str = None,
                                 new_phone_number: Annotated[str, Query(example="+000000000000", max_length=13, min_length=13)] = None,
                                 new_name: str = None,
                                 new_surname: str = None,
                                 new_patronymic: str = None,
                                 new_address: str = None
                                 ):
    validate_service_obj.validate_password(repeat_password)
    if not verify_password(repeat_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong password")
    if await user_operations.check_if_username_exists(new_username):
        raise HTTPException(status_code=400, detail="Username already exists")
    result = await user_CRUD_operations.change_user_info(current_user.username, new_username, new_password, new_email, new_phone_number, new_name, new_surname, new_patronymic, new_address)
    if result:
        return {"message": "Your info changed"}
    else:
        raise HTTPException(status_code=400, detail="Something went wrong")


@router.delete("/Delete account")
async def delete_this_account(current_user: Annotated[User, Depends(permission_operations.require_permission("account", "delete_my"))]):
    result = await user_CRUD_operations.delete_account_by_username(current_user.username)
    if result:
        return {"message" : "This account is deleted"}
    else:
        raise HTTPException(status_code=400, detail="Something went wrong")

@router.get("/Show all users")
async def show_all_users(current_user: Annotated[User, Depends(permission_operations.require_permission("users", "show_all"))]):
    result = await user_CRUD_operations.select_all_users()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Something went wrong")
