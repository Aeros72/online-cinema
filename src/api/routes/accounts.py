from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user
from src.db.session import get_db
from src.schemas.accounts import (
    UserResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenPairResponse,
    AccessTokenResponse,
    RefreshTokenRequest,
    ResendActivationRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from src.services.accounts import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
    activate_user,
    resend_activation_token,
    request_password_reset,
    confirm_password_reset
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


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db)
) -> None:
    await logout_user(
        db=db,
        refresh_token=data.refresh_token
    )


@router.get("/activate")
async def activate(
        token: str = Query(...),
        db: AsyncSession = Depends(get_db)
):
    await activate_user(db=db, token=token)
    return {"message": "Account activated"}


@router.post("/activation/resend")
async def resend_activation(
        data: ResendActivationRequest,
        db: AsyncSession = Depends(get_db)
):
    await resend_activation_token(db=db, email=data.email)
    return {"message": "Activation token has been resent."}


@router.post("/password/reset")
async def reset_password_request(
        data: PasswordResetRequest,
        db: AsyncSession = Depends(get_db)
):
    await request_password_reset(db=db, email=data.email)
    return {"message": "If account exists, reset link sent."}


@router.post("/password/reset/confirm")
async def reset_password_confirm(
        data: PasswordResetConfirmRequest,
        db: AsyncSession = Depends(get_db)
):
    await confirm_password_reset(
        db=db,
        token=data.token,
        new_password=data.new_password
    )
    return {"message": "Password has been reset."}
