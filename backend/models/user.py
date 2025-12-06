from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(100), unique=True, nullable=False, index=True)
    registered_at = Column(DateTime, default=func.now())
    is_author_verified = Column(Boolean, default=False)
    avatar_url = Column(String(255), nullable=True)
    role = Column(String(20), default="user")  # "user", "admin"
    password_hash = Column(String(255), nullable=True)
