from fastapi import Depends, HTTPException
from sqlalchemy import select

from app.api.dependencies import get_password_hash, get_current_active_user

from app.db.database import async_session_factory

from app.models.user import User, User_In_DB, UserORM



class Permission:
    PERMISSION = {
        "admin" :{"users" : ["show_all", "delete_any", "disable_user", "manage_role"],
                  "cards" : ["add_my", "show_my", "delete_my", "unfreeze_my", "show_all", "delete_any", "unfreeze_any"],
                  "transactions" : ["make_payment", "show_for_my_card", "show_all", "delete_any"],
                  "account" : ["show_info", "change_info", "delete_my", "logout"],
                  "check":["health_check"]},
        "manager" :{"users" : ["show_all"],
                  "cards" : ["add_my", "show_my", "delete_my", "unfreeze_my", "show_all"],
                  "transactions" : ["make_payment", "show_for_my_card", "show_all"],
                  "account" : ["show_info", "change_info", "delete_my", "logout"]},
        "user" : {"cards" : ["add_my", "show_my", "delete_my", "unfreeze_my"],
                  "transactions" : ["make_payment", "show_for_my_card"],
                  "account" : ["show_info", "change_info", "delete_my", "logout"]}
    }


    @classmethod
    async def check_permission(cls, user : User, resource : str, action : str):
        user_role = getattr(user, 'role', 'user')

        if user_role not in cls.PERMISSION:
            return False

        role_permissions = cls.PERMISSION[user_role]

        if resource not in role_permissions:
            return False

        return action in role_permissions[resource]

    @staticmethod
    def require_permission(resource : str, action : str):
        async def permission_dependency(current_user: User = Depends(get_current_active_user)):
            if not await Permission.check_permission(current_user, resource, action):
                raise HTTPException(status_code=403, detail="Not enough permissions")
            return current_user

        return permission_dependency


    @staticmethod
    async def create_first_admin():
        async with async_session_factory() as session:
            stmt = select(UserORM).where(UserORM.role == "admin")
            result = await session.execute(stmt)
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print("Admin is here")
                return

            #change as soon as possible
            admin = UserORM(username="admin",
                               hashed_password=get_password_hash("adminqwerty"),
                               email="admin",
                               name="System",
                               surname="Administrator",
                               patronymic="",
                               phone_number="",
                               address="System",
                               disabled=False,
                               role="admin")
            session.add(admin)
            await session.commit()
            print("Admin was created")


permission_operations = Permission()