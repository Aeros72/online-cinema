from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, asc, desc, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.movies import (
    Genre,
    Star,
    Director,
    Certification,
    Movie,
    favorite_movies,
    Rating,
    Comment
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


async def get_movies(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        year: int | None = None,
        min_imdb: float | None = None,
        genre_id: int | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
) -> list[Movie]:
    query = select(Movie)

    if search:
        query = query.where(
            or_(
                Movie.name.ilike(f"%{search}%"),
                Movie.description.ilike(f"%{search}%")
            )
        )

    if year is not None:
        query = query.where(Movie.year == year)

    if min_imdb is not None:
        query = query.where(Movie.imdb >= min_imdb)

    if genre_id is not None:
        query = query.join(Movie.genres).where(Genre.id == genre_id)

    allowed_sort_fields = {
        "id": Movie.id,
        "price": Movie.price,
        "year": Movie.year,
        "imdb": Movie.imdb,
        "votes": Movie.votes
    }

    sort_column = allowed_sort_fields.get(sort_by)

    if sort_column is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field."
        )

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_movie_by_uuid(db: AsyncSession, movie_uuid: UUID) -> Movie:
    result = await db.execute(
        select(Movie).where(Movie.uuid == movie_uuid)
    )

    movie = result.scalar_one_or_none()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found."
        )

    return movie


async def add_movie_to_favorites(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID
) -> Movie:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        select(favorite_movies).where(
            favorite_movies.c.user_id == user_id,
            favorite_movies.c.movie_id == movie.id
        )
    )
    existing = result.first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie already in favorites."
        )

    await db.execute(
        favorite_movies.insert().values(
            user_id=user_id,
            movie_id=movie.id
        )
    )

    await db.commit()
    return movie


async def remove_movie_from_favorites(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID
) -> None:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        favorite_movies.delete().where(
            favorite_movies.c.user_id == user_id,
            favorite_movies.c.movie_id == movie.id
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie is not in favorites."
        )

    await db.commit()


async def get_favorite_movies(
        db: AsyncSession,
        user_id: int
) -> list[Movie]:
    result = await db.execute(
        select(Movie)
        .join(favorite_movies, favorite_movies.c.movie_id == Movie.id)
        .where(favorite_movies.c.user_id == user_id)
    )
    return list(result.scalars().all())


async def rate_movie(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID,
        value: int
) -> Rating:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.movie_id == movie.id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.value = value
        await db.commit()
        await db.refresh(existing)
        return existing

    rating = Rating(
        user_id=user_id,
        movie_id=movie.id,
        value=value
    )

    db.add(rating)
    await db.commit()
    await db.refresh(rating)

    return rating


async def delete_rating(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID
) -> None:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.movie_id == movie.id
        )
    )
    rating = result.scalar_one_or_none()

    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found."
        )

    await db.delete(rating)
    await db.commit()


async def get_movie_rating_stats(
        db: AsyncSession,
        movie_id: int
) -> tuple[float | None, int]:
    result = await db.execute(
        select(
            func.avg(Rating.value),
            func.count(Rating.id)
        ).where(Rating.movie_id == movie_id)
    )

    average_rating, ratings_count = result.one()

    return (
        round(float(average_rating), 2) if average_rating is not None else None,
        ratings_count
    )


async def create_comment(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID,
        text: str
) -> Comment:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    comment = Comment(
        user_id=user_id,
        movie_id=movie.id,
        text=text
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


async def get_movie_comments(
        db: AsyncSession,
        movie_uuid: UUID
) -> list[Comment]:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        select(Comment)
        .where(Comment.movie_id == movie.id)
        .order_by(Comment.created_at.desc())
    )

    return list(result.scalars().all())


async def delete_comment(
        db: AsyncSession,
        user_id: int,
        comment_id: int
) -> None:
    comment = await db.get(Comment, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own comments."
        )

    await db.delete(comment)
    await db.commit()
