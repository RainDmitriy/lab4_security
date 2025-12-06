from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.comment import Comment
from repositories.base import Repository

from typing import Optional

class CommentRepository(Repository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int):
        result = await self.db.execute(select(Comment).where(Comment.id == id))
        return result.scalars().first()

    async def list(self, news_id: Optional[int] = None):
        if news_id:
             result = await self.db.execute(select(Comment).where(Comment.news_id == news_id))
        else:
             result = await self.db.execute(select(Comment))
        return result.scalars().all()

    async def create(self,  data):
        comment = Comment(**data)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def update(self, id: int,  data):
        comment = await self.get(id)
        if comment:
            for key, value in data.items():
                setattr(comment, key, value)
            await self.db.commit()
            await self.db.refresh(comment)
        return comment

    async def delete(self, id: int):
        comment = await self.get(id)
        if comment:
            await self.db.delete(comment)
            await self.db.commit()
        return comment
