from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from database import get_db
from cache import get_redis
from services.news_service import NewsService
from schemas.news import NewsCreate, NewsUpdate, NewsResponse
from models.user import User
from auth.resolvers import get_news_or_404_with_permission, verify_user_can_create_news
from models.news import News
from repositories.news_repository import NewsRepository

router = APIRouter()

async def get_news_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> NewsService:
    news_repo = NewsRepository(db, redis)
    return NewsService(news_repo)


@router.post("/news", response_model=NewsResponse)
async def create_news(
    news_data: NewsCreate,
    current_user: User = Depends(verify_user_can_create_news),
    service: NewsService = Depends(get_news_service)
):
    news = await service.create_news(current_user, news_data.dict())
    return news

@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
    service: NewsService = Depends(get_news_service)
):
    news = await service.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@router.get("/news")
async def list_news(
    service: NewsService = Depends(get_news_service)
):
    return await service.list_news()

@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_data: NewsUpdate,
    news: News = Depends(get_news_or_404_with_permission),
    service: NewsService = Depends(get_news_service)
):
    updated_news = await service.update_news(news, news_data.dict(exclude_unset=True))
    return updated_news

@router.delete("/news/{news_id}")
async def delete_news(
    news_id: int,
    news: News = Depends(get_news_or_404_with_permission),
    service: NewsService = Depends(get_news_service)
):
    await service.delete_news(news)
    return {"message": "News deleted"}
