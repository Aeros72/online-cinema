from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models.movies import (
    Genre,
    Star,
    Director,
    Certification
)


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


async def create_star(db: AsyncSession, name: str) -> Star:
    result = await db.execute(select(Star).where(Star.name == name))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Star already exists."
        )

    star = Star(name=name)

    db.add(star)
    await db.commit()
    await db.refresh(star)

    return star


async def get_stars(db: AsyncSession) -> list[Star]:
    result = await db.execute(select(Star))
    return list(result.scalars().all())


async def create_director(db: AsyncSession, name: str) -> Director:
    result = await db.execute(select(Director).where(Director.name == name))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Director already exists."
        )

    director = Director(name=name)

    db.add(director)
    await db.commit()
    await db.refresh(director)

    return director


async def get_directors(db: AsyncSession) -> list[Director]:
    result = await db.execute(select(Director))
    return list(result.scalars().all())


async def create_certification(db: AsyncSession, name: str) -> Certification:
    result = await db.execute(select(Certification).where(Certification.name == name))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Certification already exists."
        )

    certification = Certification(name=name)

    db.add(certification)
    await db.commit()
    await db.refresh(certification)

    return certification


async def get_certifications(db: AsyncSession) -> list[Certification]:
    result = await db.execute(select(Certification))
    return list(result.scalars().all())
