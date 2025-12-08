from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

from controllers.user_controller import router as user_router
from controllers.news_controller import router as news_router
from controllers.comment_controller import router as comment_router
from controllers.auth_controller import router as auth_router
from controllers.oauth import router as oauth_router


app = FastAPI()

allow_origins = [str(url).rstrip("/") for url in settings.BACKEND_CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix="/api/v1")
app.include_router(news_router, prefix="/api/v1")
app.include_router(comment_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(oauth_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "News API is running!"}
