from datetime import timezone, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import User, UserGroup, UserGroupEnum, RefreshToken, ActivationToken
from src.schemas.accounts import UserRegisterRequest, UserLoginRequest
from src.services.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expires_at,
    hash_password,
    verify_password, create_activation_token
)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_default_user_group(db: AsyncSession) -> UserGroup:
    result = await db.execute(
        select(UserGroup).where(UserGroup.name == UserGroupEnum.USER)
    )
    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default user group does not exist."
        )

    return group


async def register_user(db: AsyncSession, data: UserRegisterRequest) -> User:
    existing_user = await get_user_by_email(db=db, email=data.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )

    user_group = await get_default_user_group(db=db)

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        is_active=False,
        group_id=user_group.id
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    activation_token = ActivationToken(
        user_id=user.id,
        token=create_activation_token(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )

    db.add(activation_token)
    await db.commit()
    await db.refresh(user)

    print(f"Activation token: {activation_token.token}")

    return user


async def login_user(db: AsyncSession, data: UserLoginRequest) -> dict[str, str]:
    user = await get_user_by_email(db=db, email=data.email)

    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active."
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token()

    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=get_refresh_token_expires_at()
    )

    db.add(db_refresh_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict[str, str]:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_refresh_token = result.scalar_one_or_none()

    if db_refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    if db_refresh_token.expires_at < datetime.now(timezone.utc):
        await db.delete(db_refresh_token)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired."
        )

    access_token = create_access_token(user_id=db_refresh_token.user_id)

    return {"access_token": access_token}


async def logout_user(db: AsyncSession, refresh_token: str) -> None:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_refresh_token = result.scalar_one_or_none()

    if db_refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    await db.delete(db_refresh_token)
    await db.commit()


async def activate_user(db: AsyncSession, token: str) -> None:
    result = await db.execute(
        select(ActivationToken).where(ActivationToken.token == token)
    )
    db_token = result.scalar_one_or_none()

    if db_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activation token."
        )

    if db_token.expires_at < datetime.now(timezone.utc):
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation token expired."
        )

    user = await db.get(User, db_token.user_id)
    user.is_active = True

    await db.delete(db_token)
    await db.commit()
