from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(JSONB, nullable=False)
    published_at = Column(DateTime, default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_url = Column(String(255), nullable=True)
