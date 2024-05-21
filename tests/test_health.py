import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/healthz/")

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.text == '"ok"'
