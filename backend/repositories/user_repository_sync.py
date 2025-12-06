from datetime import datetime

from sqlalchemy.orm import Session
import redis
from sqlalchemy import select
from models.user import User
from repositories.base import Repository
from config import settings
import json
import logging

logger = logging.getLogger("uvicorn")


class UserRepositorySync(Repository):
    def __init__(self, db: Session, redis: redis.Redis):
        self.db = db
        self.redis = redis

    # Нужно там, где важна up-to-date информация о пользователе
    # Например, при проверке существования перед update
    def get(self, id: int):
        result = self.db.execute(select(User).where(User.id == id))
        user = result.scalars().first()

        logger.info(f"[DB QUERY, cache restricted] User {id} получен из БД")
        return user

    # Используется для вывода нечувствительной информации (профиль),
    # а также для проверки ролей в зависимостях
    def get_cached(self, id: int):
        cache_key = f"user:{id}"
        cached_data = self.redis.get(cache_key)
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
                password_hash=""  # безопасно: не возвращаем хеш
            )
            return user

        result = self.db.execute(select(User).where(User.id == id))
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
            "role": user.role,
        }

        self.redis.set(cache_key, json.dumps(data_to_cache), ex=settings.USER_CACHE_TTL)
        logger.info(f"[CACHE SET] User {id} сохранён в Redis на {settings.USER_CACHE_TTL}s")

        return user

    # Используется для авторизации — требуется актуальность, не из кэша
    def get_by_login(self, login: str):
        result = self.db.execute(select(User).where(User.login == login))
        user = result.scalars().first()
        return user

    def list(self):
        result = self.db.execute(select(User))
        return result.scalars().all()

    def create(self, data) -> User:
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, id: int, data):
        user = self.get(id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, id: int):
        user = self.get(id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
