"""Content submission and status endpoints."""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.message_queue import publish_content_submitted
from src.api.rate_limiter import get_rate_limiter
from src.api.repositories import create_content, get_content_status, content_exists
from src.api.schemas import (
    ContentSubmitRequest,
    ContentSubmitResponse,
    ContentStatusResponse,
)
from src.common.config import settings
from src.common.database import async_session_maker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/content", tags=["content"])


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def verify_api_key(x_api_key: str | None = Header(None)) -> None:
    """Optional API key verification."""
    if settings.api_key and settings.api_key != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@router.post(
    "/submit",
    response_model=ContentSubmitResponse,
    status_code=202,
    summary="Submit content for moderation",
)
async def submit_content(
    body: ContentSubmitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> ContentSubmitResponse:
    """
    Submit content for moderation.

    - Applies rate limiting per userId (configurable tokens per minute).
    - Returns 202 Accepted with contentId if accepted.
    - Returns 429 Too Many Requests if rate-limited.
    """
    rate_limiter = get_rate_limiter()
    if rate_limiter.check_and_apply_rate_limit(body.userId):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Too many requests.",
        )

    content = await create_content(db, body.userId, body.text)

    try:
        await publish_content_submitted(content.id, body.text, body.userId)
    except Exception as e:
        logger.exception("Failed to publish event, content saved: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to queue content for moderation.",
        )

    return ContentSubmitResponse(contentId=content.id)


@router.get(
    "/{content_id}/status",
    response_model=ContentStatusResponse,
    summary="Get moderation status",
)
async def get_status(
    content_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ContentStatusResponse:
    """
    Get the moderation status of content.

    Returns 200 with status (PENDING, APPROVED, REJECTED).
    Returns 404 if contentId does not exist.
    """
    exists = await content_exists(db, content_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Content not found")

    status = await get_content_status(db, content_id)
    if status is None:
        status = "PENDING"

    return ContentStatusResponse(contentId=content_id, status=status)
