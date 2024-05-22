import typing
from contextlib import ExitStack

import fastapi
import pytest
import pytest_asyncio
import sqlalchemy as sa
import sqlalchemy_utils as sa_utils
from httpx import ASGITransport, AsyncClient
from pytest_factoryboy import register

from app import db, deps
from app.config import settings
from app.db import Base
from app.main import app as actual_app
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
async def db_session(setup_db):
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
    actual_app.dependency_overrides[deps.get_chat_bot] = override_dependency(
        "get_chat_bot"
    )


register(factories.BotFactory)
