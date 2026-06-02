from pydantic import BaseModel


class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str
