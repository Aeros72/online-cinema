from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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
    CertificationCreate
)
from src.services.movies import (
    get_genres,
    create_genre,
    get_stars,
    create_star,
    get_directors,
    create_director,
    get_certifications,
    create_certification
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
    return [GenreResponse.model_validate(g) for g in genres]


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
    return [StarResponse.model_validate(s) for s in stars]


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
    return [DirectorResponse.model_validate(d) for d in directors]


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
    return [CertificationResponse.model_validate(c) for c in certifications]
