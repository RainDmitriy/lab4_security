from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    text: str
    news_id: int

class CommentUpdate(BaseModel):
    text: Optional[str] = None

class CommentResponse(BaseModel):
    id: int
    text: str
    news_id: int
    author_id: int
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
