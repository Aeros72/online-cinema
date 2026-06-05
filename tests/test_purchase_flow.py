import uuid
from unittest.mock import patch

import pytest

from tests.helpers import (
    auth_headers,
    fake_send_email,
    register_activate_login_admin,
    register_activate_login_user,
)


async def create_test_movie(client, admin_headers):
    suffix = uuid.uuid4().hex

    genre_response = await client.post(
        "/api/v1/movies/genres",
        json={"name": f"Genre {suffix}"},
        headers=admin_headers,
    )
    assert genre_response.status_code == 201

    star_response = await client.post(
        "/api/v1/movies/stars",
        json={"name": f"Actor {suffix}"},
        headers=admin_headers,
    )
    assert star_response.status_code == 201

    director_response = await client.post(
        "/api/v1/movies/directors",
        json={"name": f"Director {suffix}"},
        headers=admin_headers,
    )
    assert director_response.status_code == 201

    certification_response = await client.post(
        "/api/v1/movies/certifications",
        json={"name": f"PG-13 {suffix}"},
        headers=admin_headers,
    )
    assert certification_response.status_code == 201

    movie_response = await client.post(
        "/api/v1/movies",
        json={
            "name": f"Purchase Flow Movie {suffix}",
            "year": 2024,
            "time": 100,
            "imdb": 8.0,
            "votes": 500,
            "meta_score": 75,
            "gross": 100000,
            "description": "Movie for purchase flow test",
            "price": "12.99",
            "certification_id": certification_response.json()["id"],
            "genre_ids": [genre_response.json()["id"]],
            "star_ids": [star_response.json()["id"]],
            "director_ids": [director_response.json()["id"]],
        },
        headers=admin_headers,
    )
    assert movie_response.status_code == 201

    return movie_response.json()


@pytest.mark.asyncio
async def test_user_can_add_movie_to_cart_create_order_and_pay(client):
    admin = await register_activate_login_admin(client)
    admin_headers = auth_headers(admin["access_token"])

    user = await register_activate_login_user(client)
    user_headers = auth_headers(user["access_token"])

    movie = await create_test_movie(client, admin_headers)

    cart_response = await client.post(
        f"/api/v1/cart/items/{movie['uuid']}",
        headers=user_headers,
    )

    assert cart_response.status_code == 201
    assert len(cart_response.json()["items"]) == 1

    order_response = await client.post(
        "/api/v1/orders",
        headers=user_headers,
    )

    assert order_response.status_code == 201
    assert order_response.json()["status"] == "pending"
    assert order_response.json()["total_amount"] == "12.99"

    order_id = order_response.json()["id"]

    with patch("src.services.payments.send_email", fake_send_email):
        payment_response = await client.post(
            f"/api/v1/payments/orders/{order_id}",
            headers=user_headers,
        )

    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "successful"
    assert payment_response.json()["amount"] == "12.99"

    payments_response = await client.get(
        "/api/v1/payments",
        headers=user_headers,
    )

    assert payments_response.status_code == 200
    assert len(payments_response.json()) >= 1


@pytest.mark.asyncio
async def test_user_can_cancel_pending_order(client):
    admin = await register_activate_login_admin(client)
    admin_headers = auth_headers(admin["access_token"])

    user = await register_activate_login_user(client)
    user_headers = auth_headers(user["access_token"])

    movie = await create_test_movie(client, admin_headers)

    cart_response = await client.post(
        f"/api/v1/cart/items/{movie['uuid']}",
        headers=user_headers,
    )
    assert cart_response.status_code == 201

    order_response = await client.post(
        "/api/v1/orders",
        headers=user_headers,
    )
    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    cancel_response = await client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=user_headers,
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "canceled"


@pytest.mark.asyncio
async def test_user_can_refund_successful_payment(client):
    admin = await register_activate_login_admin(client)
    admin_headers = auth_headers(admin["access_token"])

    user = await register_activate_login_user(client)
    user_headers = auth_headers(user["access_token"])

    movie = await create_test_movie(client, admin_headers)

    cart_response = await client.post(
        f"/api/v1/cart/items/{movie['uuid']}",
        headers=user_headers,
    )
    assert cart_response.status_code == 201

    order_response = await client.post(
        "/api/v1/orders",
        headers=user_headers,
    )
    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    with patch("src.services.payments.send_email", fake_send_email):
        payment_response = await client.post(
            f"/api/v1/payments/orders/{order_id}",
            headers=user_headers,
        )

    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "successful"

    payment_id = payment_response.json()["id"]

    refund_response = await client.post(
        f"/api/v1/payments/{payment_id}/refund",
        headers=user_headers,
    )

    assert refund_response.status_code == 200
    assert refund_response.json()["status"] == "refunded"
