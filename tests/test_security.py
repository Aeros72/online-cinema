from src.services.security import (
    create_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_password_changes_value():
    password = "Password123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_success():
    password = "Password123"

    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_wrong_password():
    password = "Password123"

    hashed = hash_password(password)

    assert verify_password("WrongPassword123", hashed) is False


def test_refresh_token_is_generated():
    token = create_refresh_token()

    assert isinstance(token, str)
    assert len(token) > 10
