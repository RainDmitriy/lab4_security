from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from sqlalchemy.future import select
from models.news import News
from repositories.base import Repository
from config import settings
import logging
import json

logger = logging.getLogger("uvicorn")

class NewsRepository(Repository):
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis

    async def get(self, id: int):
        logger.info(f"[DB QUERY, cache restricted] News {id} получена из БД")
        result = await self.db.execute(select(News).where(News.id == id))
        news = result.scalars().first()

        return news

    async def get_cached(self, id: int):
        cache_key = f"news:{id}"

        cached_data = await self.redis.get(cache_key)
        if cached_data:
            data = json.loads(cached_data) 

            logger.info(f"[CACHE HIT] News {id} получена из Redis")
            news = News(
                id=data["id"],
                title=data["title"],
                content=data["content"],
                published_at=datetime.fromisoformat(data["published_at"]) if data["published_at"] else None,
                author_id=data["author_id"],
                cover_url=data["cover_url"]
            )

            return news
  

        logger.info(f"[DB QUERY] News {id} получена из БД")
        result = await self.db.execute(select(News).where(News.id == id))
        news = result.scalars().first()

        # чтобы в Redis не добавлялся мусор несуществующий
        if not news:
            return None

        data_to_cache = {
            "id": news.id,
            "title": news.title,
            "content": news.content,  # Dict[str, Any]
            "published_at": news.published_at.isoformat() if news.published_at else None,
            "author_id": news.author_id,
            "cover_url": news.cover_url
        }

        logger.info(f"[CACHE SET] News {id} сохранена в Redis на {settings.NEWS_CACHE_TTL}s")
        await self.redis.set(cache_key, json.dumps(data_to_cache), ex=settings.NEWS_CACHE_TTL)

        return news

    async def get_recent(self, days: int):
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(News).where(News.published_at >= cutoff)
        )
        
        return result.scalars().all()

    async def list(self):
        result = await self.db.execute(select(News))
        return result.scalars().all()

    async def create(self,  data):
        news = News(**data)
        self.db.add(news)
        await self.db.commit()
        await self.db.refresh(news)
        return news

    async def update(self, id: int,  data):
        news = await self.get(id)
        if news:
            for key, value in data.items():
                setattr(news, key, value)
            await self.db.commit()
            await self.db.refresh(news)

        return news

    async def delete(self, id: int):
        news = await self.get(id)
        if news:
            await self.db.delete(news)
            await self.db.commit()
        return news
