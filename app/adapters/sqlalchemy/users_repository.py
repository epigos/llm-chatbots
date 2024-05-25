import uuid

import sqlalchemy as sa

from app import exceptions, models, ports

from .base_repository import BaseRepository


class UserRepository(ports.UserRepository, BaseRepository):
    """
    SQLAlchemy implementation of users repository.
    """

    async def save(self, user: models.User) -> models.User:
        await self._save(user)
        return user

    async def delete(self, user: models.User) -> None:
        await self._delete(user)

    async def get_by_username(self, username: str) -> models.User:
        table = models.User.__table__
        stmt = sa.select(models.User).where(table.c.username == username)
        db_execute = await self._session.execute(stmt)
        if not (instance := db_execute.scalars().unique().one_or_none()):
            raise exceptions.DoesNotExist("User does not exist")

        return instance

    async def get_for_update(self, pk: uuid.UUID) -> models.User:
        table = models.User.__table__
        stmt = sa.select(models.User).where(table.c.id == pk).with_for_update(of=table)
        db_execute = await self._session.execute(stmt)
        if not (instance := db_execute.scalars().unique().one_or_none()):
            raise exceptions.DoesNotExist("User does not exist")

        return instance
