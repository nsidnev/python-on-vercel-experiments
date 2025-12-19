"""Business logic for high scores"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models import HighScore


async def get_high_scores(db: AsyncSession, limit: int = 10) -> List[HighScore]:
    """Get top high scores"""
    query = select(HighScore).order_by(HighScore.score.desc()).limit(limit)
    result = await db.execute(query)
    scores = result.scalars().all()
    return list(scores)


async def create_high_score(
    db: AsyncSession, player_name: str, score: int, level: int, lines: int
) -> HighScore:
    """Create a new high score entry"""
    high_score = HighScore(
        player_name=player_name, score=score, level=level, lines=lines
    )
    db.add(high_score)
    await db.commit()
    await db.refresh(high_score)
    return high_score
