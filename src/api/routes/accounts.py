from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.accounts import (
    UserResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenPairResponse
)
from src.services.accounts import register_user, login_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
        data: UserRegisterRequest,
        db: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await register_user(db=db, data=data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPairResponse)
async def login(
        data: UserLoginRequest,
        db: AsyncSession = Depends(get_db)
) -> TokenPairResponse:
    tokens = await login_user(db=db, data=data)
    return TokenPairResponse(**tokens)