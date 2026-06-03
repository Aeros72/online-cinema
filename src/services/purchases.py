from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.purchases import PurchasedMovie


async def get_purchased_movies(db: AsyncSession, user_id: int) -> list[PurchasedMovie]:
    result = await db.execute(
        select(PurchasedMovie)
        .where(PurchasedMovie.user_id == user_id)
        .options(selectinload(PurchasedMovie.movie))
        .order_by(PurchasedMovie.purchased_at.desc())
    )

    return list(result.scalars().all())
