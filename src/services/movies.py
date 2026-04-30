from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models.movies import (
    Genre,
    Star,
    Director,
    Certification,
    Movie
)
from src.schemas.movies import MovieCreate


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


async def create_movie(db: AsyncSession, data: MovieCreate) -> Movie:
    certification = await db.get(Certification, data.certification_id)

    if certification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found."
        )

    genres_result = await db.execute(select(Genre).where(Genre.id.in_(data.genre_ids)))
    genres = list(genres_result.scalars().all())

    if len(genres) != len(set(data.genre_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more genres not found."
        )

    stars_result = await db.execute(select(Star).where(Star.id.in_(data.star_ids)))
    stars = list(stars_result.scalars().all())

    if len(stars) != len(set(data.star_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more stars not found.",
        )

    directors_result = await db.execute(
        select(Director).where(Director.id.in_(data.director_ids))
    )
    directors = list(directors_result.scalars().all())

    if len(directors) != len(set(data.director_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more directors not found.",
        )

    movie = Movie(
        name=data.name,
        year=data.year,
        time=data.time,
        imdb=data.imdb,
        votes=data.votes,
        meta_score=data.meta_score,
        gross=data.gross,
        description=data.description,
        price=data.price,
        certification_id=data.certification_id,
        genres=genres,
        stars=stars,
        directors=directors
    )

    db.add(movie)
    await db.commit()
    await db.refresh(movie)

    return movie
