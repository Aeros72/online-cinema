from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user, require_roles
from src.db.session import get_db
from src.models.accounts import UserGroupEnum
from src.schemas.cart import CartResponse
from src.services.cart import (
    add_movie_to_cart,
    clear_cart,
    get_all_carts,
    get_cart,
    remove_movie_from_cart,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
async def get_cart_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_active_user)
):
    cart = await get_cart(db=db, user_id=user.id)
    return CartResponse.model_validate(cart)


@router.post(
    "/items/{movie_uuid}",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_movie_to_cart_endpoint(
    movie_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    cart = await add_movie_to_cart(db=db, user_id=user.id, movie_uuid=movie_uuid)

    return CartResponse.model_validate(cart)


@router.delete("/items/{movie_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_movie_from_cart_endpoint(
    movie_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
) -> None:
    await remove_movie_from_cart(db=db, user_id=user.id, movie_uuid=movie_uuid)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_active_user)
) -> None:
    await clear_cart(db=db, user_id=user.id)


@router.get("/admin", response_model=list[CartResponse])
async def get_all_carts_endpoint(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles(UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN)),
):
    carts = await get_all_carts(db=db)

    return [CartResponse.model_validate(cart) for cart in carts]
