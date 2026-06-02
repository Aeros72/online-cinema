from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.accounts import User
from src.models.orders import Order, OrderStatusEnum, OrderItem
from src.models.payments import Payment, PaymentStatusEnum, PaymentItem
from src.models.purchases import PurchasedMovie
from src.services.email import send_email
from src.services.stripe_service import create_checkout_session


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

    user = await db.get(User, user_id)

    await send_email(
        to=user.email,
        subject="Payment successful",
        body=(
            f"Your payment #{payment.id} was successful.\n\n"
            f"Amount: {payment.amount}\n"
            f"Order ID: {order.id}\n\n"
            "Thank you for using Online Cinema."
        ),
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
        payment_status: PaymentStatusEnum | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None
) -> list[Payment]:
    query = select(Payment).options(selectinload(Payment.items))

    if user_id is not None:
        query = query.where(Payment.user_id == user_id)

    if payment_status is not None:
        query = query.where(Payment.status == payment_status)

    if date_from is not None:
        query = query.where(Payment.created_at >= date_from)

    if date_to is not None:
        query = query.where(Payment.created_at <= date_to)

    query = query.order_by(Payment.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def refund_payment(
        db: AsyncSession,
        user_id: int,
        payment_id: int
) -> Payment:
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
        .options(selectinload(Payment.items))
    )
    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found."
        )

    if payment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your payment."
        )

    if payment.status != PaymentStatusEnum.SUCCESSFUL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only successful payments can be refunded."
        )

    payment.status = PaymentStatusEnum.REFUNDED

    await db.commit()
    await db.refresh(payment)

    return payment


async def create_order_checkout_session(
    db: AsyncSession,
    user_id: int,
    order_id: int,
) -> dict:
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
            detail="Order not found.",
        )

    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your order.",
        )

    if order.status != OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be paid.",
        )

    actual_total_amount = sum(
        (item.movie.price for item in order.items),
        Decimal("0.00"),
    )

    if actual_total_amount != order.total_amount:
        order.total_amount = actual_total_amount

    session = await create_checkout_session(
        order_id=order.id,
        amount=float(actual_total_amount),
    )

    payment = Payment(
        user_id=user_id,
        order_id=order.id,
        status=PaymentStatusEnum.PENDING,
        amount=actual_total_amount,
        external_payment_id=session.id,
    )

    db.add(payment)
    await db.commit()

    return {
        "session_id": session.id,
        "checkout_url": session.url,
    }


async def complete_stripe_payment(
    db: AsyncSession,
    stripe_session_id: str,
) -> Payment:
    result = await db.execute(
        select(Payment)
        .where(Payment.external_payment_id == stripe_session_id)
        .options(selectinload(Payment.items))
    )
    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    if payment.status == PaymentStatusEnum.SUCCESSFUL:
        return payment

    if payment.status != PaymentStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending payments can be completed.",
        )

    result = await db.execute(
        select(Order)
        .where(Order.id == payment.order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.movie)
        )
    )
    order = result.scalar_one()

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
                user_id=payment.user_id,
                movie_id=order_item.movie_id,
            )
        )

    payment.status = PaymentStatusEnum.SUCCESSFUL
    order.status = OrderStatusEnum.PAID

    await db.commit()
    await db.refresh(payment)

    user = await db.get(User, payment.user_id)

    await send_email(
        to=user.email,
        subject="Payment successful",
        body=(
            f"Your payment #{payment.id} was successful.\n\n"
            f"Amount: {payment.amount}\n"
            f"Order ID: {order.id}\n\n"
            "Thank you for using Online Cinema."
        ),
    )

    return payment

