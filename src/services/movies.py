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
    Comment,
    MovieReaction,
    MovieReactionEnum,
    CommentLike,
    CommentReply
)
from src.models.notifications import NotificationTypeEnum
from src.models.orders import OrderItem
from src.schemas.movies import MovieCreate, MovieUpdate
from src.services.notifications import create_notification


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
        query = (
            query
            .outerjoin(Movie.stars)
            .outerjoin(Movie.directors)
            .where(
                or_(
                    Movie.name.ilike(f"%{search}%"),
                    Movie.description.ilike(f"%{search}%"),
                    Star.name.ilike(f"%{search}%"),
                    Director.name.ilike(f"%{search}%"),
                )
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
    user_id: int,
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    year: int | None = None,
    min_imdb: float | None = None,
    genre_id: int | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> list[Movie]:
    query = (
        select(Movie)
        .join(favorite_movies, favorite_movies.c.movie_id == Movie.id)
        .where(favorite_movies.c.user_id == user_id)
    )

    if search:
        query = (
            query
            .outerjoin(Movie.stars)
            .outerjoin(Movie.directors)
            .where(
                or_(
                    Movie.name.ilike(f"%{search}%"),
                    Movie.description.ilike(f"%{search}%"),
                    Star.name.ilike(f"%{search}%"),
                    Director.name.ilike(f"%{search}%"),
                )
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
        "votes": Movie.votes,
    }

    sort_column = allowed_sort_fields.get(sort_by)

    if sort_column is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field.",
        )

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    return list(result.scalars().unique().all())


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


async def react_to_movie(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID,
        reaction: MovieReactionEnum
) -> MovieReaction:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        select(MovieReaction).where(
            MovieReaction.user_id == user_id,
            MovieReaction.movie_id == movie.id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.reaction = reaction
        await db.commit()
        await db.refresh(existing)
        return existing

    new_reaction = MovieReaction(
        user_id=user_id,
        movie_id=movie.id,
        reaction=reaction
    )

    db.add(new_reaction)
    await db.commit()
    await db.refresh(new_reaction)

    return new_reaction


async def delete_movie_reaction(
        db: AsyncSession,
        user_id: int,
        movie_uuid: UUID
) -> None:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    result = await db.execute(
        select(MovieReaction).where(
            MovieReaction.user_id == user_id,
            MovieReaction.movie_id == movie.id,
        )
    )
    reaction = result.scalar_one_or_none()

    if reaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found.",
        )

    await db.delete(reaction)
    await db.commit()


async def reply_to_comment(
    db: AsyncSession,
    user_id: int,
    comment_id: int,
    text: str,
) -> CommentReply:
    comment = await db.get(Comment, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    reply = CommentReply(
        comment_id=comment_id,
        user_id=user_id,
        text=text,
    )

    db.add(reply)

    if comment.user_id != user_id:
        await create_notification(
            db=db,
            user_id=comment.user_id,
            type_=NotificationTypeEnum.COMMENT_REPLY,
            message="Someone replied to your comment.",
        )

    await db.commit()
    await db.refresh(reply)

    return reply


async def like_comment(
    db: AsyncSession,
    user_id: int,
    comment_id: int,
) -> None:
    comment = await db.get(Comment, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    result = await db.execute(
        select(CommentLike).where(
            CommentLike.user_id == user_id,
            CommentLike.comment_id == comment_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Comment already liked.",
        )

    comment_like = CommentLike(
        user_id=user_id,
        comment_id=comment_id,
    )

    db.add(comment_like)

    if comment.user_id != user_id:
        await create_notification(
            db=db,
            user_id=comment.user_id,
            type_=NotificationTypeEnum.COMMENT_LIKE,
            message="Someone liked your comment.",
        )

    await db.commit()


async def unlike_comment(
    db: AsyncSession,
    user_id: int,
    comment_id: int,
) -> None:
    result = await db.execute(
        select(CommentLike).where(
            CommentLike.user_id == user_id,
            CommentLike.comment_id == comment_id,
        )
    )
    like = result.scalar_one_or_none()

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment like not found.",
        )

    await db.delete(like)
    await db.commit()


async def update_movie(
    db: AsyncSession,
    movie_uuid: UUID,
    data: MovieUpdate,
) -> Movie:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)
    update_data = data.model_dump(exclude_unset=True)

    simple_fields = {
        "name",
        "year",
        "time",
        "imdb",
        "votes",
        "meta_score",
        "gross",
        "description",
        "price",
        "certification_id",
    }

    if "certification_id" in update_data:
        certification = await db.get(Certification, update_data["certification_id"])
        if certification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certification not found.",
            )

    for field in simple_fields:
        if field in update_data:
            setattr(movie, field, update_data[field])

    if "genre_ids" in update_data:
        genres_result = await db.execute(
            select(Genre).where(Genre.id.in_(update_data["genre_ids"]))
        )
        genres = list(genres_result.scalars().all())

        if len(genres) != len(set(update_data["genre_ids"])):
            raise HTTPException(status_code=404, detail="One or more genres not found.")

        movie.genres = genres

    if "star_ids" in update_data:
        stars_result = await db.execute(
            select(Star).where(Star.id.in_(update_data["star_ids"]))
        )
        stars = list(stars_result.scalars().all())

        if len(stars) != len(set(update_data["star_ids"])):
            raise HTTPException(status_code=404, detail="One or more stars not found.")

        movie.stars = stars

    if "director_ids" in update_data:
        directors_result = await db.execute(
            select(Director).where(Director.id.in_(update_data["director_ids"]))
        )
        directors = list(directors_result.scalars().all())

        if len(directors) != len(set(update_data["director_ids"])):
            raise HTTPException(
                status_code=404,
                detail="One or more directors not found.",
            )

        movie.directors = directors

    await db.commit()
    await db.refresh(movie)

    return movie


async def delete_movie(
    db: AsyncSession,
    movie_uuid: UUID,
) -> None:
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)

    order_item_result = await db.execute(
        select(OrderItem).where(OrderItem.movie_id == movie.id)
    )
    order_item = order_item_result.scalar_one_or_none()

    if order_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete purchased movie.",
        )

    await db.delete(movie)
    await db.commit()


async def get_genres_with_movie_counts(
        db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(
            Genre.id,
            Genre.name,
            func.count(Movie.id).label("movies_count")
        )
        .outerjoin(Genre.movies)
        .group_by(Genre.id)
        .order_by(Genre.name)
    )

    rows = result.all()

    return [
        {
            "id": row.id,
            "name": row.name,
            "movies_count": row.movies_count,
        }
        for row in rows
    ]


async def update_genre(db: AsyncSession, genre_id: int, name: str) -> Genre:
    genre = await db.get(Genre, genre_id)

    if genre is None:
        raise HTTPException(status_code=404, detail="Genre not found.")

    existing_result = await db.execute(
        select(Genre).where(Genre.name == name, Genre.id != genre_id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(status_code=409, detail="Genre already exists.")

    genre.name = name
    await db.commit()
    await db.refresh(genre)

    return genre


async def delete_genre(db: AsyncSession, genre_id: int) -> None:
    genre = await db.get(Genre, genre_id)

    if genre is None:
        raise HTTPException(status_code=404, detail="Genre not found.")

    result = await db.execute(
        select(Movie)
        .join(Movie.genres)
        .where(Genre.id == genre_id)
    )
    movie = result.scalar_one_or_none()

    if movie is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete genre that is used by movies.",
        )

    await db.delete(genre)
    await db.commit()


async def update_star(db: AsyncSession, star_id: int, name: str) -> Star:
    star = await db.get(Star, star_id)

    if star is None:
        raise HTTPException(status_code=404, detail="Star not found.")

    existing_result = await db.execute(
        select(Star).where(Star.name == name, Star.id != star_id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(status_code=409, detail="Star already exists.")

    star.name = name
    await db.commit()
    await db.refresh(star)

    return star


async def delete_star(db: AsyncSession, star_id: int) -> None:
    star = await db.get(Star, star_id)

    if star is None:
        raise HTTPException(status_code=404, detail="Star not found.")

    result = await db.execute(
        select(Movie)
        .join(Movie.stars)
        .where(Star.id == star_id)
    )
    movie = result.scalar_one_or_none()

    if movie is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete star that is used by movies.",
        )

    await db.delete(star)
    await db.commit()


async def update_director(db: AsyncSession, director_id: int, name: str) -> Director:
    director = await db.get(Director, director_id)

    if director is None:
        raise HTTPException(status_code=404, detail="Director not found.")

    existing_result = await db.execute(
        select(Director).where(Director.name == name, Director.id != director_id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(status_code=409, detail="Director already exists.")

    director.name = name
    await db.commit()
    await db.refresh(director)

    return director


async def delete_director(db: AsyncSession, director_id: int) -> None:
    director = await db.get(Director, director_id)

    if director is None:
        raise HTTPException(status_code=404, detail="Director not found.")

    result = await db.execute(
        select(Movie)
        .join(Movie.directors)
        .where(Director.id == director_id)
    )
    movie = result.scalar_one_or_none()

    if movie is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete director that is used by movies.",
        )

    await db.delete(director)
    await db.commit()


async def update_certification(
    db: AsyncSession,
    certification_id: int,
    name: str,
) -> Certification:
    certification = await db.get(Certification, certification_id)

    if certification is None:
        raise HTTPException(status_code=404, detail="Certification not found.")

    existing_result = await db.execute(
        select(Certification).where(
            Certification.name == name,
            Certification.id != certification_id,
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(status_code=409, detail="Certification already exists.")

    certification.name = name
    await db.commit()
    await db.refresh(certification)

    return certification


async def delete_certification(db: AsyncSession, certification_id: int) -> None:
    certification = await db.get(Certification, certification_id)

    if certification is None:
        raise HTTPException(status_code=404, detail="Certification not found.")

    result = await db.execute(
        select(Movie).where(Movie.certification_id == certification_id)
    )
    movie = result.scalar_one_or_none()

    if movie is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete certification that is used by movies.",
        )

    await db.delete(certification)
    await db.commit()
