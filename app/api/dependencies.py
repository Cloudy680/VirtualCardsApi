from datetime import datetime, timedelta, timezone
from typing import Annotated

import re
import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.security import pwd_context, oauth2_scheme, TokenData, token_blacklist

from app.models.user import User, user_operations

from app.crud.user import user_CRUD_operations


def check_if_active(user : User):
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

def verify_password(plain_password : str, hashed_password : str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password : str):
    return pwd_context.hash(password)


async def get_user(email: str):
    if await user_operations.check_if_email_exists(email):
        user_from_db = await user_CRUD_operations.get_user_by_email(email)
        return user_from_db
    else:
        return None


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if token_blacklist.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt.decode(token,
                             settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM],
                             options={"verify_exp": True}
                             )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    check_if_active(current_user)
    return current_user

