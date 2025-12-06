from repositories.comment_repository import CommentRepository
from repositories.news_repository import NewsRepository
from fastapi import HTTPException

from models.comment import Comment
from models.user import User
from models.news import News

from typing import Optional

class CommentService:
    def __init__(self, comment_repo: CommentRepository, news_repo: NewsRepository):
        self.comment_repo = comment_repo
        self.news_repo = news_repo

    async def create_comment(self, current_user: User,  data):
        author_id = current_user.id
        news_id = data["news_id"]
        data["author_id"] = author_id

        news = await self.news_repo.get(news_id)

        if not news:
            raise HTTPException(status_code=404, detail="News not found")

        return await self.comment_repo.create(data)

    async def get_comment(self, comment_id: int):
        return await self.comment_repo.get(comment_id)

    async def list_comments(self, news_id: Optional[int] = None):
        return await self.comment_repo.list(news_id=news_id)

    async def update_comment(self, comment: Comment, data):
        comment_id = comment.id
        # author_id и news_id не должны меняться
        data.pop("author_id", None)
        data.pop("news_id", None)
        return await self.comment_repo.update(comment_id, data)

    async def delete_comment(self, comment: Comment):
        comment_id = comment.id
        return await self.comment_repo.delete(comment_id)
