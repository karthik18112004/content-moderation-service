"""Redis Pub/Sub consumer for ContentSubmitted events."""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.config import settings
from src.common.database import async_session_maker
from src.common.models import ModerationResult
from src.processor.moderation import moderate_content

logger = logging.getLogger(__name__)


async def process_message(payload: dict) -> None:
    """
    Process a ContentSubmitted event.

    Payload: {"contentId": "<UUID>", "text": "<content_text>", "userId": "<user_id>"}
    """
    try:
        content_id_str = payload.get("contentId")
        text = payload.get("text", "")
        user_id = payload.get("userId", "")

        if not content_id_str:
            logger.error("Invalid payload: missing contentId")
            return

        content_id = uuid.UUID(content_id_str)
    except (ValueError, TypeError) as e:
        logger.error("Invalid payload: %s", e)
        return

    status = moderate_content(text)

    async with async_session_maker() as session:
        try:
            stmt = (
                update(ModerationResult)
                .where(ModerationResult.content_id == content_id)
                .values(
                    status=status,
                    moderated_at=datetime.now(timezone.utc),
                )
            )
            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount == 0:
                logger.warning("No moderation result found for content_id=%s", content_id)
            else:
                logger.info(
                    "Updated moderation result for content_id=%s: status=%s",
                    content_id,
                    status,
                )
        except Exception as e:
            logger.exception("Failed to update moderation result: %s", e)
            await session.rollback()
            raise


async def run_consumer() -> None:
    """Subscribe to Redis channel and process events."""
    client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    pubsub = client.pubsub()
    channel = settings.moderation_events_channel
    await pubsub.subscribe(channel)

    logger.info("Subscribed to channel: %s", channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    await process_message(payload)
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON in message: %s", e)
                except Exception as e:
                    logger.exception("Error processing message: %s", e)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await client.close()


def main() -> None:
    """Entry point for the processor."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
