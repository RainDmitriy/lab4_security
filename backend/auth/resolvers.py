from fastapi import Depends, HTTPException
from models.news import News
from models.comment import Comment
from models.user import User
from repositories.news_repository import NewsRepository
from repositories.comment_repository import CommentRepository
from repositories.user_repository import UserRepository
from database import get_db
from cache import get_redis
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from auth.auth import get_current_user
from models.user import User


async def get_news_or_404(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> News:
    repo = NewsRepository(db, redis)
    news = await repo.get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

async def get_news_or_404_with_permission(
    news: News = Depends(get_news_or_404),
    current_user: User = Depends(get_current_user)
):
    if news.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    return news


async def get_comment_or_404(
    comment_id: int,
    db: AsyncSession = Depends(get_db)
) -> Comment:
    repo = CommentRepository(db)
    comment = await repo.get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

async def get_comment_or_404_with_permission(
    comment: Comment = Depends(get_comment_or_404),
    current_user: User = Depends(get_current_user)
):
    if comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    return comment

async def verify_user_can_create_news(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_author_verified and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only verified authors can create news")
    return current_user

async def get_user_or_404(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> User:
    repo = UserRepository(db, redis)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_user_or_404_with_permission(
    user: User = Depends(get_user_or_404),  # из запроса
    current_user: User = Depends(get_current_user)  # из токена
):
    # Проверяем, что текущий пользователь — либо сам пользователь, либо админ
    if user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    return user
