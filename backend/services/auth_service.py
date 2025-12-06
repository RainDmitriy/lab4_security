from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError

from config import settings
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from models.user import User
from utils.password import verify_password, hash_password
from auth.auth import create_access_token, create_refresh_token

import re
import secrets

LOGIN_REGEX = re.compile(r"^[a-zA-Z0-9._-]{3,32}$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
)

class AuthService:
    def __init__(self, user_repo: UserRepository, refresh_token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    async def register(self, data: dict, user_agent: str) -> User:
        login = data.get("login")
        password = data.get("password")
    
        if not login or not LOGIN_REGEX.match(login):
            raise HTTPException(
                status_code=422,
                detail="Логин должен быть 3-32 символа: латиница, цифры, ., _, -"
            )

        existing_user = await self.user_repo.get_by_login(login)
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

        data.setdefault("is_author_verified", False)
        data.setdefault("role", "user")

        return await self.user_repo.create(data)

    async def login(self, login: str, password: str, user_agent: str):
        user = await self.user_repo.get_by_login(login)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        token_data = {
            "user_id": user.id,
            "login": user.login,
            "role": user.role,
            "is_author_verified": user.is_author_verified
        }
        access_token = create_access_token(token_data)
        refresh_token_str, refresh_token_jwt = create_refresh_token(token_data)

        await self.refresh_token_repo.create(
            user_id=user.id,
            token=refresh_token_str,
            meta={"user_agent": user_agent, "created_at": datetime.utcnow().isoformat()}
        )

        return access_token, refresh_token_jwt

    async def refresh_access_token(self, refresh_token_jwt: str, user_agent: str):
        try:
            payload = jwt.decode(refresh_token_jwt, settings.REFRESH_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user_login = payload.get("login")
            user_role = payload.get("role")
            user_is_author_verified = payload.get("is_author_verified")
            jti = payload.get("jti")
            if not user_id or not jti:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        token_data = await self.refresh_token_repo.get(jti)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        await self.refresh_token_repo.delete(user_id=user_id, token=jti, blacklist=True)

        new_token_data = {
            "user_id": user_id,
            "login": user_login,
            "role": user_role,
            "is_author_verified": user_is_author_verified
        }
        new_access_token = create_access_token(new_token_data)
        new_refresh_token_str, new_refresh_token_jwt = create_refresh_token(new_token_data)

        await self.refresh_token_repo.create(
            user_id=user_id,
            token=new_refresh_token_str,
            meta={"user_agent": user_agent, "created_at": datetime.utcnow().isoformat()}
        )

        return new_access_token, new_refresh_token_jwt

    async def logout(self, refresh_token_jwt: str):
        if not refresh_token_jwt:
            return {"detail": "No refresh token provided"}
        try:
            payload = jwt.decode(refresh_token_jwt, settings.REFRESH_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            jti = payload.get("jti")
            if user_id and jti:
                await self.refresh_token_repo.delete(user_id=user_id, token=jti, blacklist=True)
        except JWTError:
            pass

    async def get_user_sessions(self, user_id: int):
        tokens = await self.refresh_token_repo.get_user_sessions(user_id)
        sessions = []
        for token in tokens:
            token_data = await self.refresh_token_repo.get(token)
            if token_data:
                sessions.append({
                    "token": token,
                    "user_agent": token_data.get("user_agent"),
                    "created_at": token_data.get("created_at")
                })
        return sessions

    async def oauth_login(self, user_info, user_agent: str):
        user = await self.user_repo.get_by_login(user_info.email)
        if not user:
            random_password = secrets.token_urlsafe(32)
            user = await self.user_repo.create({
                "login": user_info.email,
                "password_hash": hash_password(random_password),
                "avatar_url": getattr(user_info, "picture", None),
                "role": "user",
                "is_author_verified": False
            })

        token_data = {
            "user_id": user.id,
            "login": user.login,
            "role": user.role,
            "is_author_verified": user.is_author_verified
        }
        access_token = create_access_token(token_data)
        refresh_token_str, refresh_token_jwt = create_refresh_token(token_data)

        await self.refresh_token_repo.create(
            user_id=user.id,
            token=refresh_token_str,
            meta={"user_agent": user_agent, "created_at": datetime.utcnow().isoformat()}
        )

        return access_token, refresh_token_jwt
