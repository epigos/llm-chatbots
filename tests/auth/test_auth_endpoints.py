import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.helpers import auth

pytestmark = pytest.mark.asyncio

base_path = "/auth"


async def test_login_validation_errors(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.post(f"{base_path}/login/", data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text

    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "username"]
    assert data["detail"][0]["msg"] == "Field required"

    assert data["detail"][1]["loc"] == ["body", "password"]
    assert data["detail"][1]["msg"] == "Field required"


async def test_login_invalid_password_raises_error(
    client: AsyncClient, db_session: AsyncSession, user_db: models.User
) -> None:
    response = await client.post(
        f"{base_path}/login/",
        data={"username": user_db.username, "password": "invalid"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text

    data = response.json()
    assert data["message"] == "Incorrect username or password"


async def test_login_successfull(
    client: AsyncClient, db_session: AsyncSession, user_db: models.User
) -> None:
    response = await client.post(
        f"{base_path}/login/",
        data={"username": user_db.username, "password": "password"},
    )

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"] == auth.create_access_token(user_db.username)
    assert data["refresh_token"] == auth.create_refresh_token(user_db.username)


async def test_register_user_validation_errors(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.post(f"{base_path}/register/", json={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text

    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "username"]
    assert data["detail"][0]["msg"] == "Field required"

    assert data["detail"][1]["loc"] == ["body", "name"]
    assert data["detail"][1]["msg"] == "Field required"

    assert data["detail"][2]["loc"] == ["body", "password"]
    assert data["detail"][2]["msg"] == "Field required"


async def test_register_user_already_exists_errors(
    client: AsyncClient, db_session: AsyncSession, user_db: models.User
) -> None:
    response = await client.post(
        f"{base_path}/register/",
        json={
            "username": user_db.username,
            "password": "password",
            "name": user_db.name,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT, response.text

    data = response.json()
    assert data["message"] == "Database conflicts"


async def test_register_user_successfull(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    create_data = {
        "username": "email@example.org",
        "password": "password",
        "name": "name",
    }
    response = await client.post(f"{base_path}/register/", json=create_data)

    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    assert data["username"] == create_data["username"]
    assert data["name"] == create_data["name"]
