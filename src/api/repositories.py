"""Repository layer for database operations."""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.models import Content, ModerationResult

logger = logging.getLogger(__name__)


async def create_content(
    session: AsyncSession,
    user_id: str,
    text: str,
    content_id: Optional[uuid.UUID] = None,
) -> Content:
    """Create a new content record and initial moderation result."""
    content = Content(
        id=content_id or uuid.uuid4(),
        user_id=user_id,
        text=text,
    )
    session.add(content)
    # Create pending moderation result
    result = ModerationResult(content_id=content.id, status="PENDING")
    session.add(result)
    await session.flush()
    logger.info("Created content id=%s for user_id=%s", content.id, user_id)
    return content


async def get_content_status(
    session: AsyncSession,
    content_id: uuid.UUID,
) -> Optional[str]:
    """Get moderation status for content. Returns None if not found."""
    stmt = select(ModerationResult.status).where(
        ModerationResult.content_id == content_id
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    return row


async def content_exists(session: AsyncSession, content_id: uuid.UUID) -> bool:
    """Check if content exists."""
    stmt = select(Content.id).where(Content.id == content_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None
