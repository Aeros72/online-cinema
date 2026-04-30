from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class GenreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GenreResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class StarCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class StarResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class DirectorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class DirectorResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class CertificationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CertificationResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class MovieCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    year: int = Field(ge=1888)
    time: int = Field(gt=0)
    imdb: float = Field(ge=0, le=10)
    votes: int = Field(ge=0)
    meta_score: float | None = Field(default=None, ge=0, le=100)
    gross: float | None = Field(default=None, ge=0)
    description: str = Field(min_length=1)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    certification_id: int
    genre_ids: list[int]
    star_ids: list[int]
    director_ids: list[int]


class MovieResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    price: Decimal
    certification_id: int

    model_config = {
        "from_attributes": True
    }
