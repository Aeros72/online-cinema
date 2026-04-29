from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models.movies import Genre


async def create_genre(db: AsyncSession, name: str) -> Genre:
    result = await db.execute(select(Genre).where(Genre.name == name))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre already exists."
        )

    genre = Genre(name=name)

    db.add(genre)
    await db.commit()
    await db.refresh(genre)

    return genre


async def get_genres(db: AsyncSession) -> list[Genre]:
    result = await db.execute(select(Genre))
    return list(result.scalars().all())
