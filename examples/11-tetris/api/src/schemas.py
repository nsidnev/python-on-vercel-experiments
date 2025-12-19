"""Pydantic schemas for request/response validation"""

from datetime import datetime
from pydantic import BaseModel, Field


class HighScoreCreateRequest(BaseModel):
    """Schema for creating a new high score (player_name comes from auth)"""

    score: int = Field(..., ge=0)
    level: int = Field(..., ge=0)
    lines: int = Field(..., ge=0)


class HighScoreResponse(BaseModel):
    """Schema for high score response"""

    id: int
    player_name: str
    score: int
    level: int
    lines: int
    created_at: datetime

    model_config = {"from_attributes": True}
