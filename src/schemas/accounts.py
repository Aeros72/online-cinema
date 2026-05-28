import re
from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.models.accounts import UserGroupEnum, GenderEnum


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")

        return value


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    group_id: int

    model_config = {
        "from_attributes": True
    }


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResendActivationRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Must contain uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Must contain lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Must contain digit")

        return value


class ChangeUserGroupRequest(BaseModel):
    group: UserGroupEnum


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password_complexity(cls, value: str) -> str:
        return UserRegisterRequest.validate_password_complexity(value)


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: str | None
    last_name: str | None
    avatar: str | None
    gender: GenderEnum | None
    date_of_birth: date | None
    info: str | None

    model_config = {
        "from_attributes": True
    }


class UserProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    avatar: str | None = Field(default=None, max_length=255)
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    info: str | None = None
