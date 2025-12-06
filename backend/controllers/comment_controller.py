from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from database import get_db
from cache import get_redis
from services.comment_service import CommentService
from repositories.comment_repository import CommentRepository
from repositories.news_repository import NewsRepository
from schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from auth.auth import get_current_user
from models.user import User
from auth.resolvers import get_comment_or_404_with_permission
from models.comment import Comment
from models.news import News

from typing import List, Optional

router = APIRouter()

async def get_comment_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> CommentService:
    news_repo = NewsRepository(db, redis)
    comment_repo = CommentRepository(db)
    return CommentService(comment_repo, news_repo)

@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    comment = await service.create_comment(current_user, comment_data.dict())
    return comment

@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service)
):
    comment = await service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.get("/comments", response_model=List[CommentResponse])
async def list_comments(
    news_id: Optional[int] = Query(None),
    service: CommentService = Depends(get_comment_service)
):
    return await service.list_comments(news_id)

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    comment: Comment = Depends(get_comment_or_404_with_permission),
    service: CommentService = Depends(get_comment_service)
):
    updated_comment = await service.update_comment(comment, comment_data.dict(exclude_unset=True))
    return updated_comment

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    comment: Comment = Depends(get_comment_or_404_with_permission),
    service: CommentService = Depends(get_comment_service)
):
    await service.delete_comment(comment)
    return {"message": "Comment deleted"}
