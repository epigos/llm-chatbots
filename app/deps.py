import typing

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import db, ports
from app.adapters import sqlalchemy


async def get_db_session() -> typing.AsyncIterator[AsyncSession]:
    """dependency to create new database session"""
    async with db.async_db.session() as session:
        yield session


DBSession = typing.Annotated[AsyncSession, Depends(get_db_session)]


async def get_bot_repo(session: DBSession) -> ports.BotRepository:
    """dependency to create new bot repository"""
    return sqlalchemy.BotRepository(session)


BotRepository = typing.Annotated[ports.BotRepository, Depends(get_bot_repo)]
