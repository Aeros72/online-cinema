import uuid

import pytest

from tests.helpers import auth_headers, register_activate_login_admin


@pytest.mark.asyncio
async def test_admin_can_create_catalog_references(client):
    admin = await register_activate_login_admin(client)
    headers = auth_headers(admin["access_token"])

    suffix = uuid.uuid4().hex

    genre_response = await client.post(
        "/api/v1/movies/genres",
        json={"name": f"Drama {suffix}"},
        headers=headers,
    )
    assert genre_response.status_code == 201

    star_response = await client.post(
        "/api/v1/movies/stars",
        json={"name": f"Actor {suffix}"},
        headers=headers,
    )
    assert star_response.status_code == 201

    director_response = await client.post(
        "/api/v1/movies/directors",
        json={"name": f"Director {suffix}"},
        headers=headers,
    )
    assert director_response.status_code == 201

    certification_response = await client.post(
        "/api/v1/movies/certifications",
        json={"name": f"PG-13 {suffix}"},
        headers=headers,
    )
    assert certification_response.status_code == 201


@pytest.mark.asyncio
async def test_admin_can_create_movie_and_user_can_view_it(client):
    admin = await register_activate_login_admin(client)
    headers = auth_headers(admin["access_token"])

    suffix = uuid.uuid4().hex

    genre_response = await client.post(
        "/api/v1/movies/genres",
        json={"name": f"Drama {suffix}"},
        headers=headers,
    )
    star_response = await client.post(
        "/api/v1/movies/stars",
        json={"name": f"Actor {suffix}"},
        headers=headers,
    )
    director_response = await client.post(
        "/api/v1/movies/directors",
        json={"name": f"Director {suffix}"},
        headers=headers,
    )
    certification_response = await client.post(
        "/api/v1/movies/certifications",
        json={"name": f"PG-13 {suffix}"},
        headers=headers,
    )

    movie_response = await client.post(
        "/api/v1/movies",
        json={
            "name": f"Test Movie {suffix}",
            "year": 2024,
            "time": 120,
            "imdb": 8.5,
            "votes": 1000,
            "meta_score": 80,
            "gross": 1000000,
            "description": "Test movie description",
            "price": "9.99",
            "certification_id": certification_response.json()["id"],
            "genre_ids": [genre_response.json()["id"]],
            "star_ids": [star_response.json()["id"]],
            "director_ids": [director_response.json()["id"]],
        },
        headers=headers,
    )

    assert movie_response.status_code == 201

    movie = movie_response.json()

    assert movie["name"] == f"Test Movie {suffix}"
    assert movie["year"] == 2024
    assert movie["price"] == "9.99"

    movie_uuid = movie["uuid"]

    list_response = await client.get("/api/v1/movies")
    assert list_response.status_code == 200

    detail_response = await client.get(f"/api/v1/movies/{movie_uuid}")
    assert detail_response.status_code == 200
    assert detail_response.json()["uuid"] == movie_uuid
