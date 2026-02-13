"""Mock moderation logic."""
import logging
import random

logger = logging.getLogger(__name__)

# Keyword that triggers rejection
REJECT_KEYWORD = "badword"
# Probability of approval when keyword not found (e.g., 80% approved)
APPROVAL_PROBABILITY = 0.8


def moderate_content(text: str) -> str:
    """
    Simulate content moderation.

    - If text contains 'badword', returns 'REJECTED'.
    - Otherwise, randomly approves (80%) or rejects (20%).

    Returns:
        'APPROVED' or 'REJECTED'
    """
    text_lower = text.lower()
    if REJECT_KEYWORD in text_lower:
        logger.info("Content rejected: contains keyword '%s'", REJECT_KEYWORD)
        return "REJECTED"

    if random.random() < APPROVAL_PROBABILITY:
        return "APPROVED"
    return "REJECTED"
