from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.models.orders import OrderStatusEnum


class OrderItemResponse(BaseModel):
    id: int
    movie_id: int
    price_at_order: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: OrderStatusEnum
    total_amount: Decimal
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}
