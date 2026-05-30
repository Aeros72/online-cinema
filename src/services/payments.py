from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.orders import Order, OrderStatusEnum, OrderItem
from src.models.payments import Payment, PaymentStatusEnum, PaymentItem
from src.models.purchases import PurchasedMovie


async def pay_order(
        db: AsyncSession,
        user_id: int,
        order_id: int
) -> Payment:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.movie)
        )
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
            detail="Only pending orders can be paid."
        )

    actual_total_amount = sum(
        (item.movie.price for item in order.items),
        Decimal("0.00"),
    )

    if actual_total_amount != order.total_amount:
        order.total_amount = actual_total_amount

    payment = Payment(
        user_id=user_id,
        order_id=order.id,
        status=PaymentStatusEnum.SUCCESSFUL,
        amount=actual_total_amount,
        external_payment_id=f"fake_{uuid4()}",
    )

    db.add(payment)
    await db.flush()

    for order_item in order.items:
        db.add(
            PaymentItem(
                payment_id=payment.id,
                order_item_id=order_item.id,
                price_at_payment=order_item.movie.price,
            )
        )

        db.add(
            PurchasedMovie(
                user_id=user_id,
                movie_id=order_item.movie_id,
            )
        )

    order.status = OrderStatusEnum.PAID

    await db.commit()

    result = await db.execute(
        select(Payment)
        .where(Payment.id == payment.id)
        .options(selectinload(Payment.items))
    )

    return result.scalar_one()


async def get_user_payments(
        db: AsyncSession,
        user_id: int
) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .options(selectinload(Payment.items))
        .order_by(Payment.created_at.desc())
    )

    return list(result.scalars().all())


async def get_admin_payments(
        db: AsyncSession,
        user_id: int | None = None,
        payment_status: PaymentStatusEnum | None = None
) -> list[Payment]:
    query = select(Payment).options(selectinload(Payment.items))

    if user_id is not None:
        query = query.where(Payment.user_id == user_id)

    if payment_status is not None:
        query = query.where(Payment.status == payment_status)

    query = query.order_by(Payment.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())
