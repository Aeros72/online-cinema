from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.orders import OrderResponse
from src.services.orders import create_order_from_cart

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order_endpoint(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    order = await create_order_from_cart(db=db, user_id=user.id)
    return OrderResponse.model_validate(order)
