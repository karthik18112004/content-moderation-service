"""Pydantic schemas for request/response validation."""
import uuid

from pydantic import BaseModel, Field


class ContentSubmitRequest(BaseModel):
    """Request body for content submission."""

    text: str = Field(..., min_length=1, description="Content text to moderate")
    userId: str = Field(..., min_length=1, description="User identifier")

    model_config = {"json_schema_extra": {"example": {"text": "Hello world", "userId": "user123"}}}


class ContentSubmitResponse(BaseModel):
    """Response for content submission."""

    contentId: uuid.UUID = Field(..., description="Unique content identifier")

    model_config = {"json_schema_extra": {"example": {"contentId": "550e8400-e29b-41d4-a716-446655440000"}}}


class ContentStatusResponse(BaseModel):
    """Response for content status retrieval."""

    contentId: uuid.UUID = Field(..., description="Content identifier")
    status: str = Field(..., description="PENDING, APPROVED, or REJECTED")

    model_config = {
        "json_schema_extra": {
            "example": {"contentId": "550e8400-e29b-41d4-a716-446655440000", "status": "APPROVED"}
        }
    }


class ErrorResponse(BaseModel):
    """Error response body."""

    detail: str = Field(..., description="Error message")
