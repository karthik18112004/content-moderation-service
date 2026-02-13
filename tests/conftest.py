"""Pytest fixtures and configuration."""
import os

import pytest
from httpx import ASGITransport, AsyncClient

# Set test environment before importing app
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/moderation_db_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("RATE_LIMIT_TOKENS_PER_MINUTE", "10")
os.environ.setdefault("RATE_LIMIT_BUCKET_CAPACITY", "10")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def api_client():
    """Async HTTP client for API tests."""
    from src.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
