from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NewsCreate(BaseModel):
    title: str
    content: Dict[str, Any]  # JSON
    cover_url: Optional[str] = None

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    cover_url: Optional[str] = None

class NewsResponse(BaseModel):
    id: int
    title: str
    content: Dict[str, Any]
    published_at: Optional[datetime] = None
    author_id: int
    cover_url: Optional[str] = None

    class Config:
        from_attributes = True
