from fastapi import APIRouter, Request, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from database import get_db
from cache import get_redis
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from services.auth_service import AuthService
from schemas.user import UserCreate, UserResponse
from schemas.auth import LoginRequest, TokenResponse
from auth.auth import get_current_user
from models.user import User

router = APIRouter()

async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> AuthService:
    user_repo = UserRepository(db, redis)
    refresh_token_repo = RefreshTokenRepository(redis)
    return AuthService(user_repo, refresh_token_repo)

@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    user_agent = request.headers.get("user-agent", "Unknown")
    user = await service.register(user_data.dict(), user_agent)
    return user


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    try:
        login_data = LoginRequest(**await request.json())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    user_agent = request.headers.get("user-agent", "Unknown")
    access_token, refresh_token_jwt = await service.login(
        login_data.login, login_data.password, user_agent
    )

    response = TokenResponse(access_token=access_token)
    resp = Response(content=response.json())
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token_jwt,
        httponly=True,
        max_age=86400 * 30
    )
    return resp


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    refresh_token_jwt = request.cookies.get("refresh_token")
    if not refresh_token_jwt:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    user_agent = request.headers.get("user-agent", "Unknown")
    new_access_token, new_refresh_token_jwt = await service.refresh_access_token(refresh_token_jwt, user_agent)

    response = TokenResponse(access_token=new_access_token)
    resp = Response(content=response.json())
    resp.set_cookie(
        key="refresh_token",
        value=new_refresh_token_jwt,
        httponly=True,
        max_age=86400 * 30
    )
    return resp


@router.post("/auth/logout")
async def logout(
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    refresh_token_jwt = request.cookies.get("refresh_token")
    await service.logout(refresh_token_jwt)

    resp = Response(content='{"message":"Logged out"}')
    resp.set_cookie("refresh_token", "", httponly=True, max_age=0)
    return resp


@router.get("/auth/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    sessions = await service.get_user_sessions(current_user.id)
    return sessions
