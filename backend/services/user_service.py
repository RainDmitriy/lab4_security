from repositories.user_repository import UserRepository
from fastapi import HTTPException
from utils.password import hash_password

import re

LOGIN_REGEX = re.compile(r"^[a-zA-Z0-9._-]{3,32}$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
)

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self,  data):
        login = data.get("login")
        password = data.get("password")

        if not login or not LOGIN_REGEX.match(login):
            raise HTTPException(
                status_code=422,
                detail="Логин должен быть 3-32 символа: латиница, цифры, ., _, -"
            )

        existing_user = await self.repo.get_by_login(login)
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Логин уже зарегистрирован"
            )

        if not password or not PASSWORD_REGEX.match(password):
            raise HTTPException(
                status_code=422,
                detail="Пароль должен быть ≥8 символов, включать заглавные и строчные буквы, цифру и спецсимвол"
            )

        data["password_hash"] = hash_password(password)
        data.pop("password", None)

        data["is_author_verified"] = False
        data["role"] = "user"

        return await self.repo.create(data)   

    async def get_user(self, user_id: int):
        return await self.repo.get_cached(user_id)

    async def list_users(self):
        return await self.repo.list()

    async def update_user(self, user_id: int,  data):
        # Убедимся, что password не передаётся в update
        data.pop("password", None)
        data.pop("password_hash", None)
        return await self.repo.update(user_id, data)

    async def delete_user(self, user_id: int):
        return await self.repo.delete(user_id)
