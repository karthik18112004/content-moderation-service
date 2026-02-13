"""Unit tests for repository/database logic."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.repositories import create_content, get_content_status, content_exists
from src.common.models import Content, ModerationResult


@pytest.mark.asyncio
async def test_create_content_returns_content_with_id():
    """create_content creates Content and ModerationResult with PENDING status."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()

    content = await create_content(session, "user1", "Hello world")

    assert content.user_id == "user1"
    assert content.text == "Hello world"
    assert content.id is not None
    assert session.add.call_count >= 2  # Content + ModerationResult
