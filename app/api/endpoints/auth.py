from datetime import  timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter, Query
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import Token, token_blacklist, oauth2_scheme

from app.api.dependencies import get_password_hash, authenticate_user, create_access_token
from app.api.permission import permission_operations

from app.services.validate_service import validate_service_obj

from app.models.user import user_operations, User_In_DB, User

from app.crud.user import user_CRUD_operations


router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES)


@router.post("/users/sign_in")
async def sign_in(username: Annotated[str, Query(max_length = 25)],
                  password: Annotated[str, Query(description = "Password must contain: small letter, capital letter, digit, special symbol", min_length = 6)],
                  repeat_password: Annotated[str, Query(description = "Password must contain: small letter, capital letter, digit, special symbol", min_length = 6)],
                  email: str,
                  phone_number: Annotated[str, Query(example="+000000000000", max_length = 13, min_length = 13)],
                  name : str,
                  surname : str,
                  patronymic : str,
                  address: str | None = ""
                  ):
    if await user_operations.check_if_username_exists(username):
        raise HTTPException(status_code=400, detail="Username already exists")

    if password != repeat_password:
        raise HTTPException(status_code=400, detail="You repeated the password incorrectly")

    await validate_service_obj.validate_password(password)
    hashed_password = get_password_hash(password)

    await user_CRUD_operations.add_new_user(User_In_DB(username = username,
                           hashed_password =hashed_password,
                           email = email,
                           name = name,
                           surname = surname,
                           patronymic = patronymic,
                           phone_number = phone_number,
                           address = address,
                           disabled = False,
                            )
                       )

    return {"message": f"Welcome {name}!"}


@router.post("/logout")
async def logout(
        current_user: Annotated[User, Depends(permission_operations.require_permission("account", "logout"))],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        token_blacklist.add_token(token, expires_in_minutes=15)

        return {
            "message": "Successfully logged out",
            "details": "Token has been invalidated and will be rejected for 30 minutes",
            "user": current_user.username
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed: {str(e)}"
        )


