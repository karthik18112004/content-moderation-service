"""Moderation processor entry point."""
import asyncio
import logging
import sys

from src.processor.consumer import run_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the moderation processor."""
    logger.info("Starting ModerationProcessor")
    try:
        asyncio.run(run_consumer())
    except KeyboardInterrupt:
        logger.info("ModerationProcessor stopped")


if __name__ == "__main__":
    main()
