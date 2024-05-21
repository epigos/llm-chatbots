"""
Database session manager.
Inspired by: https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
"""

import contextlib
import logging
import typing

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app import config

Base = declarative_base()

logger = logging.getLogger(__name__)


class AsyncDatabase:
    """
    Async database session manager.
    """

    def __init__(self) -> None:
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self._engine: AsyncEngine | None = None

    def init(self, cfg: config.Settings) -> None:
        """
        Initialize database engine
        """
        self._engine = create_async_engine(
            cfg.database_url,
            echo=cfg.db_echo,
            pool_pre_ping=True,
            future=True,
        )
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self) -> None:
        """
        Close database and cleanup session manager
        """
        if self._engine is None:
            logger.warning("AsyncDatabase is not initialized")
            return None

        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> typing.AsyncIterator[AsyncConnection]:
        """
        Connect to database and creates connection object
        """
        if self._engine is None:
            raise RuntimeError("AsyncDatabase is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> typing.AsyncIterator[AsyncSession]:
        """
        Create database session
        """
        if self._sessionmaker is None:
            raise RuntimeError("AsyncDatabase is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async_db: AsyncDatabase = AsyncDatabase()
