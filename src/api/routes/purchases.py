from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.purchases import PurchasedMovieResponse
from src.services.purchases import get_purchased_movies

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.get("", response_model=list[PurchasedMovieResponse])
async def get_purchased_movies_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_active_user)
):
    purchases = await get_purchased_movies(db=db, user_id=user.id)
    return [PurchasedMovieResponse.model_validate(purchase) for purchase in purchases]
