from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.cart import Cart, CartItem
from src.models.movies import Movie
from src.models.purchases import PurchasedMovie


async def get_cart_with_items(db: AsyncSession, user_id: int) -> Cart | None:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.movie))
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    cart = await get_cart_with_items(db=db, user_id=user_id)

    if cart is not None:
        return cart

    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()

    cart = await get_cart_with_items(db=db, user_id=user_id)

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create cart.",
        )

    return cart


async def get_cart(db: AsyncSession, user_id: int) -> Cart:
    return await get_or_create_cart(db=db, user_id=user_id)


async def add_movie_to_cart(
    db: AsyncSession,
    user_id: int,
    movie_uuid: UUID,
) -> Cart:
    cart = await get_or_create_cart(db=db, user_id=user_id)

    result = await db.execute(select(Movie).where(Movie.uuid == movie_uuid))
    movie = result.scalar_one_or_none()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found.",
        )

    purchase_result = await db.execute(
        select(PurchasedMovie).where(
            PurchasedMovie.user_id == user_id,
            PurchasedMovie.movie_id == movie.id,
        )
    )
    purchased_movie = purchase_result.scalar_one_or_none()

    if purchased_movie is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie has already been purchased.",
        )

    existing_item = next(
        (item for item in cart.items if item.movie_id == movie.id),
        None,
    )

    if existing_item is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie already in cart.",
        )

    cart_item = CartItem(
        cart_id=cart.id,
        movie_id=movie.id,
    )

    db.add(cart_item)
    await db.commit()

    db.expire_all()

    cart = await get_cart_with_items(db=db, user_id=user_id)

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found.",
        )

    return cart


async def remove_movie_from_cart(
    db: AsyncSession,
    user_id: int,
    movie_uuid: UUID,
) -> None:
    cart = await get_or_create_cart(db=db, user_id=user_id)

    result = await db.execute(select(Movie).where(Movie.uuid == movie_uuid))
    movie = result.scalar_one_or_none()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found.",
        )

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.movie_id == movie.id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie is not in cart.",
        )

    await db.delete(item)
    await db.commit()


async def clear_cart(db: AsyncSession, user_id: int) -> None:
    cart = await get_or_create_cart(db=db, user_id=user_id)

    for item in cart.items:
        await db.delete(item)

    await db.commit()
