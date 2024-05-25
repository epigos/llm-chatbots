import contextlib
import uuid
from unittest import mock

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, ports, typings
from app.adapters import sqlalchemy, stubs
from tests import context, factories

pytestmark = pytest.mark.asyncio

base_path = "/bots"


async def test_create_bot_validation_errors(
    client: AsyncClient, db_session: AsyncSession, auth_token
) -> None:
    response = await client.post(f"{base_path}/", json={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text

    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "name"]
    assert data["detail"][0]["msg"] == "Field required"


async def test_can_create_bot(
    client: AsyncClient, db_session: AsyncSession, auth_token
) -> None:
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
    client: AsyncClient, bot_db: models.Bot, auth_token
) -> None:
    response = await client.post(f"{base_path}/", json={"name": bot_db.name})

    assert response.status_code == status.HTTP_409_CONFLICT, response.text

    data = response.json()
    assert data["message"] == "Database conflicts"


async def test_can_lists_bot(
    client: AsyncClient, db_session: AsyncSession, bot_factory, auth_token
) -> None:
    repo = sqlalchemy.BotRepository(db_session)
    bots = bot_factory.create_batch(10)
    for bot in bots:
        await repo.save(bot)

    response = await client.get(f"{base_path}/")

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert len(data) == len(bots)


async def test_can_get_bot(client: AsyncClient, bot_db: models.Bot, auth_token) -> None:
    # test not found
    response = await client.get(f"{base_path}/{uuid.uuid4()}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text

    # test get ok
    response = await client.get(f"{base_path}/{bot_db.id}/")

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert bot_db.name == data["name"]


@pytest.mark.parametrize("message,expected", [("Hello bot", "Hi, user")])
async def test_can_chat_with_bot(
    client: AsyncClient,
    bot_db: models.Bot,
    auth_token,
    message: str,
    expected: str,
) -> None:
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


async def test_can_create_bot_documents(
    client: AsyncClient,
    auth_token,
    bot_db: models.Bot,
    bot_document_factory: factories.BotDocumentFactory,
) -> None:
    docs = bot_document_factory.create_batch(5)
    payload = [
        {
            "content": doc.content,
            "filename": doc.filename,
            "content_type": "content_type",
            "metadata": {"test": "test"},
        }
        for doc in docs
    ]

    response = await client.post(f"{base_path}/{bot_db.id}/documents/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    assert len(data) == 5
    expected_docs = [
        {
            "content": doc["content"],
            "filename": doc["filename"],
            "content_type": doc["content_type"],
            "metadata": doc["doc_metadata"],
        }
        for doc in data
    ]
    assert payload == expected_docs


async def test_can_index_bot(
    client: AsyncClient,
    auth_token,
    bot_db: models.Bot,
) -> None:
    vector_store = mock.MagicMock(spec=ports.VectorStore)

    async with contextlib.AsyncExitStack() as stack:
        stack.enter_context(
            context.use_dependency(deps.get_vector_store, lambda: vector_store)
        )

        response = await client.post(f"{base_path}/{bot_db.id}/index/", json={})

    vector_store.index.assert_called_once()

    assert response.status_code == status.HTTP_202_ACCEPTED, response.text
    data = response.json()
    assert data["completed"] is False

    # test index is completed
    response = await client.get(f"{base_path}/{bot_db.id}/")

    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["data_indexed"] is True
