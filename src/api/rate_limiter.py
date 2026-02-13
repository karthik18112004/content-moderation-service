"""Token Bucket rate limiter implementation."""
import logging
import time
from typing import Dict

from src.common.config import settings

logger = logging.getLogger(__name__)


class TokenBucket:
    """
    Token Bucket rate limiter.

    - Tokens are added at a fixed rate (tokens per minute).
    - Each request consumes one token.
    - If no tokens available, the request is rate-limited.
    """

    def __init__(
        self,
        tokens_per_minute: int | None = None,
        capacity: int | None = None,
    ):
        self.tokens_per_minute = tokens_per_minute or settings.rate_limit_tokens_per_minute
        self.capacity = capacity or settings.rate_limit_bucket_capacity
        self.refill_interval = 60.0 / self.tokens_per_minute  # seconds per token
        self._buckets: Dict[str, tuple[float, float]] = {}  # user_id -> (tokens, last_refill_time)

    def _get_bucket(self, user_id: str) -> tuple[float, float]:
        """Get or create bucket for user. Returns (tokens, last_refill_time)."""
        now = time.monotonic()
        if user_id not in self._buckets:
            self._buckets[user_id] = (float(self.capacity), now)
        return self._buckets[user_id]

    def _refill_tokens(self, user_id: str) -> float:
        """Refill tokens based on elapsed time. Returns current token count."""
        tokens, last_refill = self._get_bucket(user_id)
        now = time.monotonic()
        elapsed = now - last_refill
        tokens_to_add = elapsed / self.refill_interval
        new_tokens = min(self.capacity, tokens + tokens_to_add)
        new_last_refill = last_refill + (tokens_to_add * self.refill_interval)
        self._buckets[user_id] = (new_tokens, new_last_refill)
        return new_tokens

    def check_and_apply_rate_limit(self, user_id: str) -> bool:
        """
        Check if request should be rate-limited.

        Returns:
            True if rate-limited (should reject), False if allowed.
        """
        tokens = self._refill_tokens(user_id)
        if tokens >= 1.0:
            self._buckets[user_id] = (tokens - 1.0, self._buckets[user_id][1])
            return False
        logger.warning("Rate limit exceeded for user_id=%s", user_id)
        return True


# Global rate limiter instance
_rate_limiter: TokenBucket | None = None


def get_rate_limiter() -> TokenBucket:
    """Get or create the global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TokenBucket()
    return _rate_limiter
