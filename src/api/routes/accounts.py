from fastapi import APIRouter, status, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_active_user, require_roles
from src.db.session import get_db
from src.models.accounts import UserGroupEnum
from src.schemas.accounts import (
    UserResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenPairResponse,
    AccessTokenResponse,
    RefreshTokenRequest,
    ResendActivationRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ChangeUserGroupRequest,
    ChangePasswordRequest,
    UserProfileResponse,
    UserProfileUpdateRequest
)
from src.services.accounts import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
    activate_user,
    resend_activation_token,
    request_password_reset,
    confirm_password_reset,
    activate_user_manually,
    change_user_group,
    change_password,
    get_or_create_user_profile,
    update_user_profile,
    update_user_avatar
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


@router.post(
    "/admin/users/{user_id}/activate",
    response_model=UserResponse
)
async def admin_activate_user_endpoint(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        admin=Depends(require_roles(UserGroupEnum.ADMIN))
):
    user = await activate_user_manually(db=db, user_id=user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/admin/users/{user_id}/group",
    response_model=UserResponse
)
async def admin_change_user_group_endpoint(
        user_id: int,
        data: ChangeUserGroupRequest,
        db: AsyncSession = Depends(get_db),
        admin=Depends(require_roles(UserGroupEnum.ADMIN))
):
    user = await change_user_group(
        db=db,
        user_id=user_id,
        group=data.group
    )

    return UserResponse.model_validate(user)


@router.post("/password/change")
async def change_password_endpoint(
        data: ChangePasswordRequest,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    await change_password(
        db=db,
        user=user,
        old_password=data.old_password,
        new_password=data.new_password
    )

    return {"message": "Password has been changed."}


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile_endpoint(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    profile = await get_or_create_user_profile(db=db, user_id=user.id)
    return UserProfileResponse.model_validate(profile)


@router.patch("/profile", response_model=UserProfileResponse)
async def update_profile_endpoint(
        data: UserProfileUpdateRequest,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    profile = await update_user_profile(
        db=db,
        user_id=user.id,
        data=data
    )

    return UserProfileResponse.model_validate(profile)


@router.post("/profile/avatar", response_model=UserProfileResponse)
async def upload_avatar_endpoint(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_active_user)
):
    profile = await update_user_avatar(
        db=db,
        user_id=user.id,
        file=file
    )

    return UserProfileResponse.model_validate(profile)
