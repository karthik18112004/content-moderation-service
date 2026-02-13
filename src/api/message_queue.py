"""Redis message queue for event publishing."""
import json
import logging
import uuid
from typing import Any

import redis.asyncio as redis

from src.common.config import settings

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get or create Redis connection."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def publish_content_submitted(
    content_id: uuid.UUID,
    text: str,
    user_id: str,
) -> None:
    """
    Publish ContentSubmitted event to the message queue.

    Event payload: {"contentId": "<UUID>", "text": "<content_text>", "userId": "<user_id>"}
    """
    payload = {
        "contentId": str(content_id),
        "text": text,
        "userId": user_id,
    }
    try:
        client = await get_redis()
        channel = settings.moderation_events_channel
        await client.publish(channel, json.dumps(payload))
        logger.info(
            "Published ContentSubmitted event for content_id=%s, user_id=%s",
            content_id,
            user_id,
        )
    except Exception as e:
        logger.exception("Failed to publish ContentSubmitted event: %s", e)
        raise


async def check_redis_health() -> bool:
    """Check if Redis connection is healthy."""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception as e:
        logger.error("Redis health check failed: %s", e)
        return False


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
