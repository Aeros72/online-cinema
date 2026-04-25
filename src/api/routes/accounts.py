from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.accounts import (
    UserResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenPairResponse,
    AccessTokenResponse,
    RefreshTokenRequest
)
from src.services.accounts import (
    register_user,
    login_user,
    refresh_access_token
)

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


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
        data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db)
):
    tokens = await refresh_access_token(
        db=db,
        refresh_token=data.refresh_token
    )

    return AccessTokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_active_user)) -> UserResponse:
    return UserResponse.model_validate(user)
