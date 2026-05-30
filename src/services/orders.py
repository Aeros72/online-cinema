from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.orders import Order, OrderStatusEnum, OrderItem
from src.models.cart import Cart, CartItem
from src.models.purchases import PurchasedMovie


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

    movie_ids = [item.movie_id for item in cart.items]

    purchased_result = await db.execute(
        select(PurchasedMovie.movie_id).where(
            PurchasedMovie.user_id == user_id,
            PurchasedMovie.movie_id.in_(movie_ids),
        )
    )
    purchased_movie_ids = set(purchased_result.scalars().all())

    if purchased_movie_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart contains already purchased movies.",
        )

    pending_orders_result = await db.execute(
        select(Order)
        .where(
            Order.user_id == user_id,
            Order.status == OrderStatusEnum.PENDING,
        )
        .options(selectinload(Order.items))
    )
    pending_orders = list(pending_orders_result.scalars().all())

    cart_movie_ids = set(movie_ids)

    for pending_order in pending_orders:
        pending_movie_ids = {item.movie_id for item in pending_order.items}

        if pending_movie_ids == cart_movie_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending order with the same movies.",
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


async def cancel_order(
        db: AsyncSession,
        user_id: int,
        order_id: int
) -> Order:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )

    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your order."
        )

    if order.status != OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be canceled."
        )

    order.status = OrderStatusEnum.CANCELED

    await db.commit()
    await db.refresh(order)

    return order


async def get_admin_orders(
        db: AsyncSession,
        user_id: int | None = None,
        order_status: OrderStatusEnum | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None
) -> list[Order]:
    query = select(Order).options(selectinload(Order.items))

    if user_id is not None:
        query = query.where(Order.user_id == user_id)

    if order_status is not None:
        query = query.where(Order.status == order_status)

    if date_from is not None:
        query = query.where(Order.created_at >= date_from)

    if date_to is not None:
        query = query.where(Order.created_at <= date_to)

    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())
