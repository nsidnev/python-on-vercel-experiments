"""Database models"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from api.src.database import Base


class HighScore(Base):
    """High score model for Tetris game"""

    __tablename__ = "high_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False, index=True)
    level = Column(Integer, nullable=False)
    lines = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("idx_score_desc", score.desc()),)
