from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from sqlalchemy.future import select
from models.user import User
from repositories.base import Repository
from config import settings
import json
import logging

logger = logging.getLogger("uvicorn")


class UserRepository(Repository):
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis

    # нужно там, где важна up-to-date инфа о пользователе
    # например, при проверке существования перед update
    async def get(self, id: int):
        result = await self.db.execute(select(User).where(User.id == id))
        user =  result.scalars().first()

        logger.info(f"[DB QUERY, cache restricted] User {id} получен из БД")

        return user

    # нужно для вывода нечувствительной информации о пользователе (aka профиль)
    # ещё для проверки ролей в зависимостях
    async def get_cached(self, id: int):
        cache_key = f"user:{id}"
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            logger.info(f"[CACHE HIT] User {id} получен из Redis")
            data = json.loads(cached_data)
            user = User(
                id=data["id"],
                registered_at=datetime.fromisoformat(data["registered_at"]) if data["registered_at"] else None,
                avatar_url=data["avatar_url"],
                is_author_verified=data["is_author_verified"],
                login=data["login"],
                role=data["role"],
                password_hash=""  # безопасно, чтобы не возвращать хеш
            )

            return user

        result = await self.db.execute(select(User).where(User.id == id))
        user = result.scalars().first()
        if not user:
            return None

        logger.info(f"[DB QUERY] User {id} получен из БД")
        data_to_cache = {
           "id": user.id,
           "registered_at": user.registered_at.isoformat() if user.registered_at else None,
            "avatar_url": user.avatar_url,
            "is_author_verified": user.is_author_verified,
            "login": user.login,
            "role": user.role
        }

        await self.redis.set(cache_key, json.dumps(data_to_cache), ex=settings.USER_CACHE_TTL)
        logger.info(f"[CACHE SET] User {id} сохранён в Redis на {settings.USER_CACHE_TTL}s")
        
        return user

    # используется для авторизации, поэтому важна актуальность, не из кэша
    async def get_by_login(self, login: str):
        result = await self.db.execute(select(User).where(User.login == login))
        user =  result.scalars().first()

        return user

    async def list(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def create(self, data: dict):
        user = User(**data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, id: int,  dict):
        user = await self.get(id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def delete(self, id: int):
        user = await self.get(id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
        return user
