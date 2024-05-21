import typing
from contextlib import ExitStack

import pytest
import pytest_asyncio
import sqlalchemy_utils as sa_utils
from alembic import config as alembic_config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from asyncpg import Connection
from httpx import ASGITransport, AsyncClient

from app import db, deps
from app.config import settings
from app.main import app as actual_app


@pytest.fixture
def app():
    with ExitStack():
        yield actual_app


@pytest_asyncio.fixture
async def client(app) -> typing.AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def run_migrations(connection: Connection):
    alembic_conf_file = (settings.root_dir / "alembic.ini").absolute()
    config = alembic_config.Config(
        str(alembic_conf_file),
        # We don't want an alembic-specific logger setup for tests, so skip it
        attributes={"skip_logger_setup": True},
    )
    script_location = (settings.root_dir / "migrations").absolute()
    config.set_main_option("script_location", str(script_location))
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs("head", rev)

    context = MigrationContext.configure(
        connection, opts={"target_metadata": db.Base.metadata, "fn": upgrade}
    )

    with context.begin_transaction():
        with Operations.context(context):
            context.run_migrations()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    settings.db_database = f"{settings.db_database}-test"

    database_url = str(settings.database_url.render_as_string(False)).replace(
        "+asyncpg", ""
    )

    if not sa_utils.database_exists(database_url):
        sa_utils.create_database(database_url)

    db.async_db.init(settings)
    # Run alembic migrations on test DB
    async with db.async_db.connect() as connection:
        await connection.run_sync(run_migrations)

    yield

    # Teardown
    await db.async_db.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def transactional_session():
    async with db.async_db.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            await session.rollback()  # Rolls back the outer transaction


@pytest_asyncio.fixture(scope="function")
async def db_session(transactional_session):
    yield transactional_session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def session_override(app, db_session):
    async def get_db_session_override():
        yield db_session[0]

    app.dependency_overrides[deps.get_db_session] = get_db_session_override
