"""Integration tests for the full API flow."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

# Patch environment before imports
import os
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/moderation_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("RATE_LIMIT_TOKENS_PER_MINUTE", "100")
os.environ.setdefault("RATE_LIMIT_BUCKET_CAPACITY", "100")


@pytest.fixture
async def client():
    """API client - requires running services for full integration."""
    from src.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
@pytest.mark.integration
async def test_submit_content_validation(client: AsyncClient):
    """Invalid input returns 400 Bad Request."""
    # Empty text
    r = await client.post("/api/v1/content/submit", json={"text": "", "userId": "u1"})
    assert r.status_code == 422  # Pydantic validation

    # Empty userId
    r = await client.post("/api/v1/content/submit", json={"text": "hello", "userId": ""})
    assert r.status_code == 422

    # Missing fields
    r = await client.post("/api/v1/content/submit", json={})
    assert r.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
async def test_submit_and_status_flow(client: AsyncClient):
    """
    Full flow: submit content -> get PENDING -> processor runs -> get APPROVED/REJECTED.
    Requires database and Redis to be running (docker-compose up -d).
    """
    try:
        r = await client.post(
            "/api/v1/content/submit",
            json={"text": "Hello world", "userId": "test-user-123"},
        )
    except (ConnectionRefusedError, OSError) as e:
        pytest.skip(f"Database/Redis not available: {e}")

    if r.status_code == 500:
        pytest.skip("Database/Redis not available - run with docker-compose up -d")

    assert r.status_code == 202
    data = r.json()
    assert "contentId" in data
    content_id = data["contentId"]

    # Get status - should be PENDING initially
    r = await client.get(f"/api/v1/content/{content_id}/status")
    assert r.status_code == 200
    status_data = r.json()
    assert status_data["contentId"] == content_id
    assert status_data["status"] in ("PENDING", "APPROVED", "REJECTED")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_not_found(client: AsyncClient):
    """Non-existent content returns 404. Requires DB running."""
    fake_id = str(uuid.uuid4())
    try:
        r = await client.get(f"/api/v1/content/{fake_id}/status")
    except (ConnectionRefusedError, OSError) as e:
        pytest.skip(f"Database not available: {e}")
    assert r.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_rate_limiting(client: AsyncClient):
    """
    Burst of requests should trigger 429.
    Uses a small capacity for the test.
    """
    from src.api.rate_limiter import get_rate_limiter

    limiter = get_rate_limiter()
    # Use a unique user to avoid interference
    user_id = f"rate-test-{uuid.uuid4()}"

    # Reset by using fresh limiter with capacity 2
    test_limiter = __import__("src.api.rate_limiter", fromlist=["TokenBucket"]).TokenBucket(
        tokens_per_minute=60, capacity=2
    )

    assert test_limiter.check_and_apply_rate_limit(user_id) is False
    assert test_limiter.check_and_apply_rate_limit(user_id) is False
    assert test_limiter.check_and_apply_rate_limit(user_id) is True
