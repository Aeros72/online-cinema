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
