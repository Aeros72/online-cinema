from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.orders import Order, OrderStatusEnum
from src.models.payments import Payment, PaymentStatusEnum, PaymentItem


async def pay_order(
        db: AsyncSession,
        user_id: int,
        order_id: int
) -> Payment:
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
            detail="Only pending orders can be paid."
        )

    payment = Payment(
        user_id=user_id,
        order_id=order.id,
        status=PaymentStatusEnum.SUCCESSFUL,
        amount=order.total_amount,
        external_payment_id=f"fake_{uuid4()}",
    )

    db.add(payment)
    await db.flush()

    for order_item in order.items:
        db.add(
            PaymentItem(
                payment_id=payment.id,
                order_item_id=order_item.id,
                price_at_payment=order_item.price_at_order
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
