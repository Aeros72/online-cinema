from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PurchasedMovieItemResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    year: int
    price: Decimal

    model_config = {
        "from_attributes": True,
    }


class PurchasedMovieResponse(BaseModel):
    id: int
    purchased_at: datetime
    movie: PurchasedMovieItemResponse

    model_config = {
        "from_attributes": True,
    }
