from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    login: str
    password: str
    avatar_url: Optional[str] = None
#    по принципу least priv, создание учётки делает админ
#    назначает права АИБ
#    is_author_verified: bool = False
#    role: str = "user"

class UserUpdate(BaseModel):
    avatar_url: Optional[str] = None
    is_author_verified: Optional[bool] = None
    role: Optional[str] = None
    # пароль не обновляется через PUT/PATCH

class UserResponse(BaseModel):
    id: int
    login: str
    registered_at: Optional[datetime] = None
    is_author_verified: bool
    avatar_url: Optional[str] = None
    role: str = "user"
    # password_hash не возвращается

    class Config:
        from_attributes = True
