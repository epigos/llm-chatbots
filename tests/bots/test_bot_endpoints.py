import contextlib
import uuid
from unittest import mock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, ports, typings
from app.adapters import sqlalchemy, stubs
from tests import context

pytestmark = pytest.mark.asyncio

base_path = "/bots"


async def test_create_bot_validation_errors(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.post(f"{base_path}/", json={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text

    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "name"]
    assert data["detail"][0]["msg"] == "Field required"


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


async def test_should_not_create_bot_with_existing_name(
    client: AsyncClient, db_session: AsyncSession, bot: models.Bot
) -> None:
    repo = sqlalchemy.BotRepository(db_session)
    bot_db = await repo.save(bot)

    response = await client.post(f"{base_path}/", json={"name": bot_db.name})

    assert response.status_code == status.HTTP_409_CONFLICT, response.text

    data = response.json()
    assert data["message"] == "Database conflicts"


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


@pytest.mark.parametrize("message,expected", [("Hello bot", "Hi, user")])
async def test_can_chat_with_bot(
    client: AsyncClient,
    db_session: AsyncSession,
    bot: models.Bot,
    message: str,
    expected: str,
) -> None:
    repo = sqlalchemy.BotRepository(db_session)
    bot_db = await repo.save(bot)

    payload = {"message": message, "session_id": str(uuid.uuid4())}

    stub_chatbot = stubs.ChatBotAgent(bot_db, results=expected)
    vector_store = mock.MagicMock(spec=ports.VectorStore)

    agent_repo = stubs.BotAgentRepository(stub_chatbot)
    async with contextlib.AsyncExitStack() as stack:
        stack.enter_context(
            context.use_dependency(deps.get_bot_agent_repo, lambda: agent_repo)
        )
        stack.enter_context(
            context.use_dependency(deps.get_vector_store, lambda: vector_store)
        )

        response = await client.post(f"{base_path}/{bot_db.id}/chat/", json=payload)

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert data["content"] == expected
