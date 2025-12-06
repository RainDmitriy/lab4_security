from datetime import datetime, timedelta

from sqlalchemy.orm import Session
import redis
from sqlalchemy import select
from models.news import News
from repositories.base import Repository
from config import settings
import json
import logging

logger = logging.getLogger("uvicorn")


class NewsRepositorySync(Repository):
    def __init__(self, db: Session, redis: redis.Redis):
        self.db = db
        self.redis = redis

    def get(self, id: int):
        logger.info(f"[DB QUERY, cache restricted] News {id} получена из БД")
        result = self.db.execute(select(News).where(News.id == id))
        news = result.scalars().first()
        return news

    def get_cached(self, id: int):
        cache_key = f"news:{id}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            data = json.loads(cached_data)
            logger.info(f"[CACHE HIT] News {id} получена из Redis")
            news = News(
                id=data["id"],
                title=data["title"],
                content=data["content"],
                published_at=datetime.fromisoformat(data["published_at"]) if data["published_at"] else None,
                author_id=data["author_id"],
                cover_url=data["cover_url"],
            )
            return news

        logger.info(f"[DB QUERY] News {id} получена из БД")
        result = self.db.execute(select(News).where(News.id == id))
        news = result.scalars().first()

        # Не кэшируем несуществующие новости
        if not news:
            return None

        data_to_cache = {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "published_at": news.published_at.isoformat() if news.published_at else None,
            "author_id": news.author_id,
            "cover_url": news.cover_url,
        }

        logger.info(f"[CACHE SET] News {id} сохранена в Redis на {settings.NEWS_CACHE_TTL}s")
        self.redis.set(cache_key, json.dumps(data_to_cache), ex=settings.NEWS_CACHE_TTL)

        return news

    def get_recent(self, days: int):
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = self.db.execute(
            select(News).where(News.published_at >= cutoff)
        )
        return result.scalars().all()

    def list(self):
        result = self.db.execute(select(News))
        return result.scalars().all()

    def create(self, data):
        news = News(**data)
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        return news

    def update(self, id: int, data):
        news = self.get(id)
        if news:
            for key, value in data.items():
                setattr(news, key, value)
            self.db.commit()
            self.db.refresh(news)
        return news

    def delete(self, id: int):
        news = self.get(id)
        if news:
            self.db.delete(news)
            self.db.commit()
            return True
        return False
