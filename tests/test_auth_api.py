import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.accounts import ActivationToken


async def fake_send_email(*args, **kwargs):
    return None


@pytest.mark.asyncio
async def test_register_user(client):
    email = f"test_{uuid.uuid4().hex}@example.com"

    with patch("src.services.accounts.send_email", fake_send_email):
        response = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": email,
                "password": "Password123",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_register_activate_login_flow(client):
    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "Password123"

    with patch("src.services.accounts.send_email", fake_send_email):
        register_response = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": email,
                "password": password,
            },
        )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == email
    assert register_response.json()["is_active"] is False

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ActivationToken).where(
                ActivationToken.user_id == register_response.json()["id"]
            )
        )
        activation_token = result.scalar_one()

    activate_response = await client.get(
        "/api/v1/accounts/activate",
        params={
            "token": activation_token.token,
        },
    )

    assert activate_response.status_code == 200
    assert activate_response.json()["message"] == "Account activated"

    login_response = await client.post(
        "/api/v1/accounts/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    tokens = login_response.json()

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["access_token"]
    assert tokens["refresh_token"]
