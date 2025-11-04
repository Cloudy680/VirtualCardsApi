from sqlalchemy import select

from app.core.security import pwd_context

from app.db.database import async_session_factory

from app.models.user import User, User_In_DB, UserORM


class UserCRUD:

    @staticmethod
    async def add_new_user(user: User_In_DB):
        async with async_session_factory() as session:
            new_user = UserORM(username=user.username,
                               hashed_password=user.hashed_password,
                               email=user.email,
                               name=user.name,
                               surname=user.surname,
                               patronymic=user.patronymic,
                               phone_number=user.phone_number,
                               address=user.address,
                               disabled=user.disabled,
                               role=user.role)
            session.add(new_user)
            await session.commit()

    @staticmethod
    async def get_user_by_username(username: str):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.username == username)
            user = await session.scalars(stmt)
            return user.first()

    @staticmethod
    async def get_user_by_id(user_id: int):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.id == user_id)
            user = await session.scalars(stmt)
            return user.first()

    @staticmethod
    async def select_all_users():
        async with async_session_factory() as session:
            stmt = select(UserORM)
            result = await session.execute(stmt)
            users = result.scalars().all()
            return [User.model_validate(user) for user in users]

    @staticmethod
    async def delete_account_by_username(username : str):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.username == username)
            result = await session.execute(stmt)
            user = result.scalar()

            if user:
                await session.delete(user)
                await session.commit()
                return True
            else:
                return False

    @staticmethod
    async def delete_user_by_id(user_id : int):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar()

            if user:
                await session.delete(user)
                await session.commit()
                return True
            else:
                return False

    @staticmethod
    async def change_users_activity(user_id : int):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar()

            if user:
                user.disabled = not user.disabled
                await session.commit()
                return True
            else:
                return False

    @staticmethod
    async def change_users_role(user_id : int, role: str):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar()

            if user:
                user.role = role
                await session.commit()
                return True
            else:
                return False

    @staticmethod
    async def change_user_info(username : str,
                               new_username: str = None,
                               new_password: str = None,
                               new_email: str = None,
                               new_phone_number: str = None,
                               new_name: str = None,
                               new_surname: str = None,
                               new_patronymic: str = None,
                               new_address: str = None
                               ):
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.username == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            updates = {}

            if new_username is not None:
                updates['username'] = new_username
            if new_password is not None:
                updates['hashed_password'] = pwd_context.hash(new_password)

            if new_email is not None:
                updates['email'] = new_email
            if new_phone_number is not None:
                updates['phone_number'] = new_phone_number
            if new_name is not None:
                updates['name'] = new_name
            if new_surname is not None:
                updates['surname'] = new_surname
            if new_patronymic is not None:
                updates['patronymic'] = new_patronymic
            if new_address is not None:
                updates['address'] = new_address

            for field, value in updates.items():
                setattr(user, field, value)

            await session.commit()
            return True




user_CRUD_operations = UserCRUD()