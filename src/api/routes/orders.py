from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.orders import OrderResponse
from src.services.orders import (
    create_order_from_cart,
    get_user_orders,
    cancel_order
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order_endpoint(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    order = await create_order_from_cart(db=db, user_id=user.id)
    return OrderResponse.model_validate(order)


@router.get(
    "",
    response_model=list[OrderResponse]
)
async def get_user_orders_endpoint(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    orders = await get_user_orders(db=db, user_id=user.id)
    return [OrderResponse.model_validate(order) for order in orders]


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
async def cancel_order_endpoint(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    order = await cancel_order(db=db, user_id=user.id, order_id=order_id)
    return OrderResponse.model_validate(order)
