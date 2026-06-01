import pytest
from pydantic import ValidationError

from src.schemas.accounts import UserRegisterRequest


def test_register_password_must_have_min_length():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="test@example.com",
            password="Aa1",
        )


def test_register_password_must_have_uppercase():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="test@example.com",
            password="password123",
        )


def test_register_password_must_have_lowercase():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="test@example.com",
            password="PASSWORD123",
        )


def test_register_password_must_have_digit():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="test@example.com",
            password="Password",
        )


def test_register_password_valid():
    user = UserRegisterRequest(
        email="test@example.com",
        password="Password123",
    )

    assert user.email == "test@example.com"
    assert user.password == "Password123"
