from repositories.news_repository import NewsRepository
from fastapi import HTTPException

from models.news import News
from models.user import User

class NewsService:
    def __init__(self, news_repo: NewsRepository):
        self.news_repo = news_repo

    async def create_news(self, current_user: User,  data):
        # Принудительно перезаписываем author_id из current_user
        data["author_id"] = current_user.id
        news = await self.news_repo.create(data)

        return news

    # используется для показа новостей пользователям
    # можно использовать кэшированный
    async def get_news(self, news_id: int):
        return await self.news_repo.get_cached(news_id)

    async def get_recent_news(self, days: int):
        return await self.news_repo.get_recent(days)

    async def list_news(self):
        return await self.news_repo.list()

    async def update_news(self, news: News,  data):
        news_id = news.id
        # author_id не должен меняться
        data.pop("author_id", None)
        return await self.news_repo.update(news_id, data)

    async def delete_news(self, news: News):
        news_id = news.id
        return await self.news_repo.delete(news_id)
