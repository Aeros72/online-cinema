from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.movies import (
    GenreResponse,
    GenreCreate,
    StarResponse,
    StarCreate,
    DirectorResponse,
    DirectorCreate,
    CertificationResponse,
    CertificationCreate,
    MovieResponse,
    MovieCreate,
    RatingResponse,
    RatingCreate,
    CommentResponse,
    CommentCreate
)
from src.services.movies import (
    get_genres,
    create_genre,
    get_stars,
    create_star,
    get_directors,
    create_director,
    get_certifications,
    create_certification,
    get_movies,
    create_movie,
    get_movie_by_uuid,
    add_movie_to_favorites,
    remove_movie_from_favorites,
    get_favorite_movies,
    rate_movie,
    delete_rating,
    get_movie_rating_stats,
    create_comment,
    get_movie_comments,
    delete_comment
)

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.post(
    "/genres",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_genre_endpoint(
        data: GenreCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    genre = await create_genre(db=db, name=data.name)
    return GenreResponse.model_validate(genre)


@router.get("/genres", response_model=list[GenreResponse])
async def get_genres_endpoint(
        db: AsyncSession = Depends(get_db)
):
    genres = await get_genres(db=db)
    return [GenreResponse.model_validate(genre) for genre in genres]


@router.post(
    "/stars",
    response_model=StarResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_star_endpoint(
        data: StarCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    star = await create_star(db=db, name=data.name)
    return StarResponse.model_validate(star)


@router.get("/stars", response_model=list[StarResponse])
async def get_stars_endpoint(
        db: AsyncSession = Depends(get_db)
):
    stars = await get_stars(db=db)
    return [StarResponse.model_validate(star) for star in stars]


@router.post(
    "/directors",
    response_model=DirectorResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_director_endpoint(
        data: DirectorCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    director = await create_director(db=db, name=data.name)
    return DirectorResponse.model_validate(director)


@router.get("/directors", response_model=list[DirectorResponse])
async def get_directors_endpoint(
        db: AsyncSession = Depends(get_db)
):
    directors = await get_directors(db=db)
    return [DirectorResponse.model_validate(director) for director in directors]


@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_certification_endpoint(
        data: CertificationCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    certification = await create_certification(db=db, name=data.name)
    return CertificationResponse.model_validate(certification)


@router.get("/certifications", response_model=list[CertificationResponse])
async def get_certifications_endpoint(
        db: AsyncSession = Depends(get_db)
):
    certifications = await get_certifications(db=db)
    return [CertificationResponse.model_validate(certification) for certification in certifications]


@router.post(
    "",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_movie_endpoint(
        data: MovieCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    movie = await create_movie(db=db, data=data)
    return MovieResponse.model_validate(movie)


@router.get("", response_model=list[MovieResponse])
async def get_movies_endpoint(
        page: int = Query(default=1, ge=1),
        size: int = Query(default=10, ge=1, le=100),
        search: str | None = Query(default=None),
        year: int | None = Query(default=None),
        min_imdb: float | None = Query(default=None, ge=0, le=10),
        genre_id: int | None = Query(default=None),
        sort_by: Literal["id", "price", "year", "imdb", "votes"] = "id",
        sort_order: Literal["asc", "desc"] = "asc",
        db: AsyncSession = Depends(get_db)
):
    movies = await get_movies(
        db=db,
        page=page,
        size=size,
        search=search,
        year=year,
        min_imdb=min_imdb,
        genre_id=genre_id,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return [
        await build_movie_response(movie=movie, db=db)
        for movie in movies
    ]


@router.get("/favorites", response_model=list[MovieResponse])
async def get_favorite_movies_endpoint(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    movies = await get_favorite_movies(db=db, user_id=user.id)
    return [
        await build_movie_response(movie=movie, db=db)
        for movie in movies
    ]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
) -> None:
    await delete_comment(
        db=db,
        user_id=user.id,
        comment_id=comment_id
    )


@router.get("/{movie_uuid}", response_model=MovieResponse)
async def get_movie_detail_endpoint(
        movie_uuid: UUID,
        db: AsyncSession = Depends(get_db)
):
    movie = await get_movie_by_uuid(db=db, movie_uuid=movie_uuid)
    return await build_movie_response(movie=movie, db=db)


@router.post(
    "/{movie_uuid}/favorites",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_movie_to_favorites_endpoint(
        movie_uuid: UUID,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    movie = await add_movie_to_favorites(
        db=db,
        user_id=user.id,
        movie_uuid=movie_uuid
    )

    return MovieResponse.model_validate(movie)


@router.delete("/{movie_uuid}/favorites", status_code=status.HTTP_204_NO_CONTENT)
async def remove_movie_from_favorites_endpoint(
        movie_uuid: UUID,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
) -> None:
    await remove_movie_from_favorites(
        db=db,
        user_id=user.id,
        movie_uuid=movie_uuid
    )


@router.post(
    "/{movie_uuid}/rating",
    response_model=RatingResponse
)
async def rate_movie_endpoint(
        movie_uuid: UUID,
        data: RatingCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    rating = await rate_movie(
        db=db,
        user_id=user.id,
        movie_uuid=movie_uuid,
        value=data.value
    )

    return RatingResponse.model_validate(rating)


@router.delete("/{movie_uuid}/rating", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating_endpoint(
       movie_uuid: UUID,
       db: AsyncSession = Depends(get_db),
       user=Depends(get_current_active_user)
):
    await delete_rating(
        db=db,
        user_id=user.id,
        movie_uuid=movie_uuid
    )


async def build_movie_response(
        movie,
        db: AsyncSession
) -> MovieResponse:
    average_rating, ratings_count = await get_movie_rating_stats(
        db=db,
        movie_id=movie.id
    )

    response = MovieResponse.model_validate(movie)
    response.average_rating = average_rating
    response.ratings_count = ratings_count

    return response


@router.post(
    "/{movie_uuid}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_comment_endpoint(
        movie_uuid: UUID,
        data: CommentCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    comment = await create_comment(
        db=db,
        user_id=user.id,
        movie_uuid=movie_uuid,
        text=data.text
    )

    return CommentResponse.model_validate(comment)


@router.get(
    "/{movie_uuid}/comments",
    response_model=list[CommentResponse]
)
async def get_movie_comments_endpoint(
        movie_uuid: UUID,
        db: AsyncSession = Depends(get_db)
):
    comments = await get_movie_comments(db=db, movie_uuid=movie_uuid)
    return [CommentResponse.model_validate(comment) for comment in comments]
