import uuid
from unittest.mock import patch

from httpx import AsyncClient
from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.accounts import ActivationToken, User, UserGroup, UserGroupEnum


async def fake_send_email(*args, **kwargs):
    return None


async def register_activate_login_user(
    client: AsyncClient,
    email: str | None = None,
    password: str = "Password123",
) -> dict:
    email = email or f"test_{uuid.uuid4().hex}@example.com"

    with patch("src.services.accounts.send_email", fake_send_email):
        register_response = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": email,
                "password": password,
            },
        )

    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ActivationToken).where(ActivationToken.user_id == user_id)
        )
        activation_token = result.scalar_one()

    activate_response = await client.get(
        "/api/v1/accounts/activate",
        params={"token": activation_token.token},
    )
    assert activate_response.status_code == 200

    login_response = await client.post(
        "/api/v1/accounts/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    return {
        "id": user_id,
        "email": email,
        "password": password,
        "access_token": login_response.json()["access_token"],
        "refresh_token": login_response.json()["refresh_token"],
    }


async def make_user_admin(user_id: int) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserGroup).where(UserGroup.name == UserGroupEnum.ADMIN)
        )
        admin_group = result.scalar_one()

        user = await db.get(User, user_id)
        user.group_id = admin_group.id

        await db.commit()


async def register_activate_login_admin(client: AsyncClient) -> dict:
    user = await register_activate_login_user(client)
    await make_user_admin(user["id"])

    login_response = await client.post(
        "/api/v1/accounts/login",
        json={
            "email": user["email"],
            "password": user["password"],
        },
    )
    assert login_response.status_code == 200

    user["access_token"] = login_response.json()["access_token"]
    user["refresh_token"] = login_response.json()["refresh_token"]

    return user


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}
