from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CartMovieResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    year: int
    price: Decimal

    model_config = {
        "from_attributes": True
    }


class CartItemResponse(BaseModel):
    id: int
    added_at: datetime
    movie: CartMovieResponse

    model_config = {
        "from_attributes": True
    }


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]

    model_config = {
        "from_attributes": True
    }
