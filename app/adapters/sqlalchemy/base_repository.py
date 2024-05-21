import typing

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """
    Base class for all repositories.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _delete(self, model: typing.Any) -> None:
        await self._session.delete(model)
        await self._session.flush()

    async def _save(self, model: typing.Any) -> None:
        self._session.add(model)
        try:
            await self._session.commit()
            await self._session.refresh(model)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Database conflicts") from exc
