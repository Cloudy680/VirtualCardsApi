from pydantic import BaseModel

from sqlalchemy import select, exists
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.db.database import async_session_factory


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique = True)
    hashed_password : Mapped[str] = mapped_column(nullable=False)
    email : Mapped[str] = mapped_column(nullable=False, unique = True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    patronymic: Mapped[str] = mapped_column(nullable=False)
    phone_number : Mapped[str] = mapped_column()
    address : Mapped[str] = mapped_column()
    disabled : Mapped[bool] = mapped_column(nullable=False, default=False)

    role : Mapped[str] = mapped_column(nullable=False, default="user")

class User(BaseModel):
    id: int | None = None
    username: str = None
    email: str = None
    name: str = None
    surname : str = None
    patronymic : str = None
    phone_number: str = None
    address: str | None = None
    disabled: bool = False

    role: str = "user"

    @staticmethod
    async def check_if_username_exists(username: str):
        async with async_session_factory() as session:
            stmt = select(exists().where(UserORM.username == username))
            result = await session.execute(stmt)
            return result.scalar()

    @staticmethod
    async def check_if_email_exists(email: str):
        async with async_session_factory() as session:
            stmt = select(exists().where(UserORM.email == email))
            result = await session.execute(stmt)
            return result.scalar()

    class Config:
        from_attributes = True


user_operations = User()


class User_In_DB(User):
    hashed_password: str