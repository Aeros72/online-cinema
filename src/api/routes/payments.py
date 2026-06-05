from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.dependencies.auth import get_current_active_user, require_roles
from src.core.config import settings
from src.db.session import get_db
from src.models.accounts import UserGroupEnum
from src.models.payments import PaymentStatusEnum
from src.schemas.payments import PaymentResponse
from src.schemas.stripe import CheckoutSessionResponse
from src.services.payments import (
    complete_stripe_payment,
    create_order_checkout_session,
    get_admin_payments,
    get_user_payments,
    pay_order,
    refund_payment,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/orders/{order_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def pay_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    payment = await pay_order(db=db, user_id=user.id, order_id=order_id)
    return PaymentResponse.model_validate(payment)


@router.get("", response_model=list[PaymentResponse])
async def get_user_payments_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_active_user)
):
    payments = await get_user_payments(db=db, user_id=user.id)
    return [PaymentResponse.model_validate(payment) for payment in payments]


@router.get("/admin", response_model=list[PaymentResponse])
async def get_admin_payments_endpoint(
    user_id: int | None = None,
    payment_status: PaymentStatusEnum | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles(UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN)),
):
    payments = await get_admin_payments(
        db=db,
        user_id=user_id,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
    )

    return [PaymentResponse.model_validate(payment) for payment in payments]


@router.post(
    "/orders/{order_id}/checkout",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checkout_session_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    session = await create_order_checkout_session(
        db=db,
        user_id=user.id,
        order_id=order_id,
    )

    return CheckoutSessionResponse.model_validate(session)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload.",
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature.",
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        await complete_stripe_payment(
            db=db,
            stripe_session_id=session["id"],
        )

    return {"received": True}


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment_endpoint(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    payment = await refund_payment(db=db, user_id=user.id, payment_id=payment_id)

    return PaymentResponse.model_validate(payment)
