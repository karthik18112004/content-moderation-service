"""Unit tests for mock moderation logic."""
import random
from unittest.mock import patch

import pytest

from src.processor.moderation import REJECT_KEYWORD, moderate_content


class TestModerateContent:
    """Tests for moderate_content function."""

    def test_rejects_content_with_badword(self):
        """Content containing 'badword' should be rejected."""
        assert moderate_content("This has badword in it") == "REJECTED"
        assert moderate_content("BADWORD at start") == "REJECTED"
        assert moderate_content("badword") == "REJECTED"
        assert moderate_content("Mixed Case BadWord") == "REJECTED"

    def test_approves_content_without_badword(self):
        """Content without badword - run multiple times to handle random case."""
        # When random says approve (mock it)
        with patch("src.processor.moderation.random") as mock_random:
            mock_random.random.return_value = 0.5  # < 0.8, so approved
            assert moderate_content("Clean content") == "APPROVED"

    def test_rejects_content_randomly_without_badword(self):
        """Content without badword can be randomly rejected."""
        with patch("src.processor.moderation.random") as mock_random:
            mock_random.random.return_value = 0.9  # >= 0.8, so rejected
            assert moderate_content("Clean content") == "REJECTED"

    def test_empty_string_approved_or_rejected_randomly(self):
        """Empty string follows random logic."""
        with patch("src.processor.moderation.random") as mock_random:
            mock_random.random.return_value = 0.0
            assert moderate_content("") == "APPROVED"
