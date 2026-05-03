from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.payments import PaymentResponse
from src.services.payments import pay_order

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post(
    "/orders/{order_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
async def pay_order_endpoint(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    payment = await pay_order(db=db, user_id=user.id, order_id=order_id)
    return PaymentResponse.model_validate(payment)
