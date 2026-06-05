from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user, require_roles
from src.db.session import get_db
from src.models.accounts import UserGroupEnum
from src.models.orders import OrderStatusEnum
from src.schemas.orders import OrderResponse
from src.services.orders import (
    cancel_order,
    create_order_from_cart,
    get_admin_orders,
    get_user_orders,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_active_user)
):
    order = await create_order_from_cart(db=db, user_id=user.id)
    return OrderResponse.model_validate(order)


@router.get("", response_model=list[OrderResponse])
async def get_user_orders_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_active_user)
):
    orders = await get_user_orders(db=db, user_id=user.id)
    return [OrderResponse.model_validate(order) for order in orders]


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    order = await cancel_order(db=db, user_id=user.id, order_id=order_id)
    return OrderResponse.model_validate(order)


@router.get("/admin", response_model=list[OrderResponse])
async def get_admin_orders_endpoint(
    user_id: int | None = None,
    order_status: OrderStatusEnum | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles(UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN)),
):
    orders = await get_admin_orders(
        db=db,
        user_id=user_id,
        order_status=order_status,
        date_from=date_from,
        date_to=date_to,
    )

    return [OrderResponse.model_validate(order) for order in orders]
