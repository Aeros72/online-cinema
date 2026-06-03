from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.models.payments import PaymentStatusEnum


class PaymentItemResponse(BaseModel):
    id: int
    order_item_id: int
    price_at_payment: Decimal

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    order_id: int
    created_at: datetime
    status: PaymentStatusEnum
    amount: Decimal
    external_payment_id: str | None
    items: list[PaymentItemResponse]

    model_config = {"from_attributes": True}
