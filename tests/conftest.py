import os

os.environ["ENV"] = "test"

import pytest
from httpx import ASGITransport, AsyncClient

from src.db.session import engine
from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(
        app=app,
        raise_app_exceptions=True,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    await transport.aclose()


@pytest.fixture(autouse=True)
async def dispose_engine_after_test():
    yield
    await engine.dispose()
