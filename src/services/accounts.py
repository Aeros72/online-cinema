from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import User, UserGroup, UserGroupEnum
from src.schemas.accounts import UserRegisterRequest
from src.services.security import hash_password


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

    return user
