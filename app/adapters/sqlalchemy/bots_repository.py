import typing
import uuid

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy import orm

from app import models, ports

from .base_repository import BaseRepository


class BotRepository(ports.BotRepository, BaseRepository):
    """
    SQLAlchemy implementation of bots repository.
    """

    async def save(self, bot: models.Bot) -> models.Bot:
        await self._save(bot)
        return bot

    async def delete(self, bot: models.Bot) -> None:
        await self._delete(bot)

    async def get_all(self) -> list[models.Bot]:
        stmt = sa.select(models.Bot).options(orm.selectinload(models.Bot.contexts))
        db_execute = await self._session.execute(stmt)
        results = db_execute.scalars().all()

        return typing.cast(list[models.Bot], results)

    async def get_by_id(self, pk: uuid.UUID) -> models.Bot:
        table = models.Bot.__table__
        stmt = (
            sa.select(models.Bot)
            .where(table.c.id == pk)
            .options(orm.selectinload(models.Bot.contexts))
            .execution_options(populate_existing=True)
        )
        db_execute = await self._session.execute(stmt)
        if not (instance := db_execute.scalars().unique().one_or_none()):
            raise HTTPException(status_code=404, detail="Bot does not exist")

        return instance

    async def get_for_update(self, pk: uuid.UUID) -> models.Bot:
        table = models.Bot.__table__
        stmt = (
            sa.select(models.Bot)
            .where(table.c.id == pk)
            .options(orm.selectinload(models.Bot.contexts))
            .with_for_update(of=table)
        )
        db_execute = await self._session.execute(stmt)
        if not (instance := db_execute.scalars().unique().one_or_none()):
            raise HTTPException(status_code=404, detail="Bot does not exist")

        return instance
