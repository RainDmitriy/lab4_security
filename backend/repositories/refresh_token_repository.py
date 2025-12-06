import json
from redis.asyncio import Redis
from datetime import timedelta
from config import settings

class RefreshTokenRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create(self, user_id: int, token: str, meta: dict = None):
        meta = meta or {}
        key = f"user_id:refresh:{token}"
        await self.redis.setex(key, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), json.dumps({
            "user_id": user_id,
            "token": token,
            **meta
        }))

        # Добавляем токен в безвременный список активных
        await self.redis.sadd(f"user_id:sessions:{user_id}", token)

    async def get(self, token: str):
        token_data = await self.redis.get(f"user_id:refresh:{token}")
        if not token_data:
            return None

        user_id = json.loads(token_data)["user_id"]
        blacklisted = await self.redis.exists(f"token:blacklist:{user_id}:{token}")
        if blacklisted:
            return None
        return json.loads(token_data)

    async def delete(self, user_id: int, token: str, blacklist: bool = False):
        await self.redis.delete(f"user_id:refresh:{token}")
        await self.redis.srem(f"user_id:sessions:{user_id}", token)
        if blacklist:
            await self.redis.setex(
                f"token:blacklist:{user_id}:{token}",
                timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                "revoked"
            )

    async def get_user_sessions(self, user_id: int):
        tokens = await self.redis.smembers(f"user_id:sessions:{user_id}")
        return list(tokens)

