import stripe

from src.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_checkout_session(
    order_id: int,
    amount: float,
) -> stripe.checkout.Session:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Order #{order_id}",
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )

    return session
