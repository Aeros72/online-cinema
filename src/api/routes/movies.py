from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.movies import GenreResponse, GenreCreate
from src.services.movies import get_genres, create_genre

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
    return [GenreResponse.model_validate(g) for g in genres]
