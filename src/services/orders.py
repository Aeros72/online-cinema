from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.orders import Order, OrderStatusEnum, OrderItem
from src.models.cart import Cart, CartItem


async def get_user_cart_with_items(
        db: AsyncSession,
        user_id: int
) -> Cart | None:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.movie))
    )

    return result.scalar_one_or_none()


async def create_order_from_cart(
        db: AsyncSession,
        user_id: int
) -> Order:
    cart = await get_user_cart_with_items(db=db, user_id=user_id)

    if cart is None or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty."
        )

    total_amount = sum(
        (item.movie.price for item in cart.items),
        Decimal("0.00")
    )

    order = Order(
        user_id=user_id,
        status=OrderStatusEnum.PENDING,
        total_amount=total_amount
    )

    db.add(order)
    await db.flush()

    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            movie_id=item.movie_id,
            price_at_order=item.movie.price
        )
        db.add(order_item)

    for item in cart.items:
        await db.delete(item)

    await db.commit()

    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    created_order = result.scalar_one()

    return created_order


async def get_user_orders(
        db: AsyncSession,
        user_id: int
) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )

    return list(result.scalars().all())
