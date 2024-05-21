import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import typings
from app.adapters import sqlalchemy

pytestmark = pytest.mark.asyncio

base_path = "/bots"


async def test_can_create_bot(client: AsyncClient, db_session: AsyncSession) -> None:
    create_data = {
        "name": "test",
        "welcome_message": "test message",
        "contexts": [
            {"role": typings.BotContextRole.system, "content": "test content"}
        ],
    }
    response = await client.post(f"{base_path}/", json=create_data)

    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    assert data["name"] == create_data["name"]
    assert data["welcome_message"] == create_data["welcome_message"]
    assert create_data["contexts"] == [
        {"role": ctx["role"], "content": ctx["content"]} for ctx in data["contexts"]
    ]


async def test_can_lists_bot(
    client: AsyncClient, db_session: AsyncSession, bot_factory
) -> None:
    repo = sqlalchemy.BotRepository(db_session)
    bots = bot_factory.create_batch(10)
    for bot in bots:
        await repo.save(bot)

    response = await client.get(f"{base_path}/")

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert len(data) == len(bots)
