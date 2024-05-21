import typing

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import db


async def get_db_session() -> typing.AsyncIterator[AsyncSession]:
    """dependency to create new database session"""
    async with db.async_db.session() as session:
        yield session


DBSession = typing.Annotated[AsyncSession, Depends(get_db_session)]
