"""API service entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.message_queue import check_redis_health, close_redis
from src.api.routers.content import router as content_router
from src.common.config import settings
from src.common.database import check_db_health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    yield
    await close_redis()
    logger.info("API service shutting down")


app = FastAPI(
    title="Content Moderation API",
    description="API for submitting content for moderation and retrieving status",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content_router)


@app.get("/health")
async def health():
    """Health check endpoint for Docker and load balancers."""
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    status = "healthy" if (db_ok and redis_ok) else "unhealthy"
    return {
        "status": status,
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
