from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from repositories.user_repository import UserRepository
from database import get_db
from cache import get_redis
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse
from auth.auth import get_current_user, get_current_admin
from models.user import User
from auth.resolvers import get_user_or_404_with_permission

router = APIRouter()

async def get_user_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> UserService:
    user_repo = UserRepository(db, redis)
    return UserService(user_repo)

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    # создать пользователя может только админ
    current_user: User = Depends(get_current_admin), 
    service: UserService = Depends(get_user_service)
):
    user = await service.create_user(user_data.dict())
    return user

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    # получить пользователя может только админ или сам пользователь
    # не акутально, в виду front, теперь даём всем имена
    # user: User = Depends(get_user_or_404_with_permission),
    service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    return user

@router.get("/users")
async def list_users(
    # получить список пользователей может только админ
    current_user: User = Depends(get_current_admin),
    service: UserService = Depends(get_user_service)
):
    return await service.list_users()

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update_data: UserUpdate,
    # обновить пользователя может только админ или сам пользователь
    user: User = Depends(get_user_or_404_with_permission),
    service: UserService = Depends(get_user_service)
):
    updated_user = await service.update_user(user.id, user_update_data.dict(exclude_unset=True))
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    # удалить пользователя может только админ или сам пользователь
    user: User = Depends(get_user_or_404_with_permission),
    service: UserService = Depends(get_user_service)
):
    await service.delete_user(user.id)
    return {"message": "User deleted"}
