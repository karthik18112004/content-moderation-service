"""Unit tests for Token Bucket rate limiter."""
import time

import pytest

from src.api.rate_limiter import TokenBucket


class TestTokenBucket:
    """Tests for TokenBucket rate limiter."""

    def test_allows_requests_within_limit(self):
        """Within capacity, all requests should be allowed."""
        limiter = TokenBucket(tokens_per_minute=60, capacity=5)
        for _ in range(5):
            assert limiter.check_and_apply_rate_limit("user1") is False

    def test_rate_limits_after_capacity_exhausted(self):
        """After exhausting capacity, requests should be rate-limited."""
        limiter = TokenBucket(tokens_per_minute=60, capacity=3)
        for _ in range(3):
            assert limiter.check_and_apply_rate_limit("user1") is False
        assert limiter.check_and_apply_rate_limit("user1") is True

    def test_per_user_limiting(self):
        """Each user has independent rate limit."""
        limiter = TokenBucket(tokens_per_minute=60, capacity=2)
        assert limiter.check_and_apply_rate_limit("user1") is False
        assert limiter.check_and_apply_rate_limit("user1") is False
        assert limiter.check_and_apply_rate_limit("user1") is True

        assert limiter.check_and_apply_rate_limit("user2") is False
        assert limiter.check_and_apply_rate_limit("user2") is False
        assert limiter.check_and_apply_rate_limit("user2") is True

    def test_tokens_refill_over_time(self):
        """Tokens should refill over time."""
        # 1 token per second refill
        limiter = TokenBucket(tokens_per_minute=60, capacity=2)
        assert limiter.check_and_apply_rate_limit("user1") is False
        assert limiter.check_and_apply_rate_limit("user1") is False
        assert limiter.check_and_apply_rate_limit("user1") is True

        time.sleep(1.1)  # Allow 1 token to refill
        assert limiter.check_and_apply_rate_limit("user1") is False
        assert limiter.check_and_apply_rate_limit("user1") is True
