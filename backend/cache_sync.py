import redis
from config import settings
from typing import Optional, Generator

redis_client: Optional[redis.Redis] = None

def init_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        # Тестовое подключение
        redis_client.ping()
    return redis_client

def get_redis() -> Generator[redis.Redis, None, None]:
    global redis_client
    if redis_client is None:
        init_redis()
    yield redis_client
