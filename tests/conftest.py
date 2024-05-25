import typing
from contextlib import ExitStack
from unittest.mock import patch

import fastapi
import pytest
import pytest_asyncio
import sqlalchemy as sa
import sqlalchemy_utils as sa_utils
from httpx import ASGITransport, AsyncClient
from langchain_openai import ChatOpenAI
from moto import mock_aws
from pytest_factoryboy import register
from sqlalchemy.ext.asyncio import AsyncSession

from app import db, deps, models
from app.adapters.sqlalchemy import BotRepository, UserRepository
from app.config import settings
from app.db import Base
from app.main import app as actual_app
from app.utils import get_s3_client
from tests import factories


@pytest.fixture
def app() -> typing.Generator[fastapi.FastAPI, None, None]:
    with ExitStack():
        yield actual_app


@pytest_asyncio.fixture
async def client(app) -> typing.AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
def setup_db(request):
    default_db = settings.db_database

    settings.db_database = f"{settings.db_database}-test"

    database_url = str(settings.database_url.render_as_string(False)).replace(
        "+asyncpg", ""
    )

    if not sa_utils.database_exists(database_url):
        sa_utils.create_database(database_url)

    engine = sa.create_engine(url=database_url)

    # Run alembic migrations on test DB
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    yield

    Base.metadata.drop_all(engine)
    settings.db_database = default_db


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db) -> AsyncSession:
    db.async_db.init(settings)

    async with db.async_db.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            await session.rollback()  # Rolls back the outer transaction

    await db.async_db.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def session_override(app, db_session):
    async def get_db_session_override():
        yield db_session

    app.dependency_overrides[deps.get_db_session] = get_db_session_override


def override_dependency(name):
    """
    Default dependency override for to ensure test isolation
    for dependencies making external API calls.
    """

    def overridden_dependency():
        raise RuntimeError(f"You must override a dependency: {name}")

    return overridden_dependency


@pytest.fixture(autouse=True, scope="session")
def override_dependencies() -> None:
    """Override external deps to ensure test isolation of dependencies."""
    actual_app.dependency_overrides[deps.get_bot_agent_repo] = override_dependency(
        "get_bot_agent_repo"
    )
    actual_app.dependency_overrides[deps.get_embeddings] = override_dependency(
        "get_embeddings"
    )
    actual_app.dependency_overrides[deps.get_vector_store] = override_dependency(
        "get_vector_store"
    )


@pytest.fixture(autouse=True, scope="session")
def mock_chat_open_ai():
    with patch.object(ChatOpenAI, "__init__") as mock_init:
        mock_init.return_value = None
        yield mock_init


@pytest.fixture
def s3_bucket() -> str:
    with mock_aws():
        s3 = get_s3_client()
        s3.create_bucket(Bucket=settings.s3_uploads_bucket_name)
        yield settings.s3_uploads_bucket_name


@pytest_asyncio.fixture
async def user_db(user: models.User, db_session: AsyncSession) -> models.User:
    repo = UserRepository(db_session)
    user.set_password_hash("password")

    user_obj = await repo.save(user)
    return user_obj


@pytest.fixture
def auth_token(app) -> None:
    def _get_token() -> str:
        yield "test"

    original_value = app.dependency_overrides.get(deps.get_token)
    app.dependency_overrides[deps.get_token] = _get_token

    yield

    if original_value is None:
        del app.dependency_overrides[deps.get_token]
    else:
        app.dependency_overrides[deps.get_token] = original_value


@pytest_asyncio.fixture
async def bot_db(bot: models.Bot, db_session: AsyncSession) -> models.Bot:
    repo = BotRepository(db_session)
    bot_db = await repo.save(bot)
    return bot_db


register(factories.BotFactory)
register(factories.BotContextFactory)
register(factories.BotDocumentFactory)
register(factories.UserFactory)
