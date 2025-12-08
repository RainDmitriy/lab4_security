from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    NEWS_CACHE_TTL: int = 300
    USER_CACHE_TTL: int = 300
    MAX_RETRIES: int = 5
    DEBUG: bool = False

    PORT: int = 8000
    HOST: str = "0.0.0.0"

    LOG_LEVEL: str = "info"        # debug, info, warning, error, critical
    ACCESS_LOG: bool = True 

    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536    # 64 MiB
    ARGON2_PARALLELISM: int = 1

    @field_validator(
        "SECRET_KEY",
        "REFRESH_SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "GITHUB_CLIENT_ID",
        "GITHUB_CLIENT_SECRET"
    )
    def must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Required environment variable is missing.")
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def parse_cors_list(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception as e:
                    raise ValueError(f"Cannot parse JSON list: {v}") from e
            return v.split()
        return v


settings = Settings()
