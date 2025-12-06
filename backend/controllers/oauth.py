from fastapi import APIRouter, Request, Depends, Response
from schemas.auth import LoginRequest, TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from cache import get_redis
from redis.asyncio import Redis
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from config import settings

from fastapi_sso.sso.github import GithubSSO

router = APIRouter()

sso = GithubSSO(
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    redirect_uri="http://127.0.0.1:8000/api/v1/auth/github/callback",
)

async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> AuthService:
    user_repo = UserRepository(db, redis)
    refresh_token_repo = RefreshTokenRepository(redis)
    return AuthService(user_repo, refresh_token_repo)

# --- OAuth Login (redirect to GitHub) ---
@router.get("/auth/github")
async def github_login():
    return await sso.get_login_redirect()

# --- OAuth Callback ---
@router.get("/auth/github/callback")
async def github_callback(request: Request, db: AsyncSession = Depends(get_db), service: AuthService = Depends(get_auth_service)):
    user_info = await sso.verify_and_process(request)
    user_agent = request.headers.get("user-agent", "Unknown")
    access_token, refresh_token_jwt = await service.oauth_login(user_info, user_agent)

    response = TokenResponse(access_token=access_token)
    resp = Response(content=response.json())
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token_jwt,
        httponly=True,
        max_age=86400 * 30
    )

    return resp
