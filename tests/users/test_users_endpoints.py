import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.helpers import auth

pytestmark = pytest.mark.asyncio

base_path = "/users"


async def test_get_user_invalid_token_raises_error(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.get(f"{base_path}/me/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text

    data = response.json()
    assert data["message"] == "Not authenticated"

    response = await client.get(
        f"{base_path}/me/", headers={"Authorization": "Bearer fake"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text

    data = response.json()
    assert data["message"] == "Could not validate credentials"


async def test_get_user_valid_token_with_non_existent_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = auth.create_access_token("user@non-existent.org")

    response = await client.get(
        f"{base_path}/me/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text

    data = response.json()
    assert data["message"] == "Invalid user credentials"


async def test_can_get_user(client: AsyncClient, user_db: models.User) -> None:
    token = auth.create_access_token(user_db.username)

    response = await client.get(
        f"{base_path}/me/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert data["username"] == user_db.username
