import abc
import uuid

from app import models


class BotRepository(abc.ABC):
    """
    Abstract class for bot repositories.
    """

    @abc.abstractmethod
    async def save(self, bot: models.Bot) -> models.Bot:
        """Save bot model to database"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, bot: models.Bot) -> None:
        """Deletes bot model from database"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all(self) -> list[models.Bot]:
        """Returns all bot models from database"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_id(self, pk: uuid.UUID) -> models.Bot:
        """Returns bot a single bot model from database
        based on pk or raises 404 if not found"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_for_update(self, pk: uuid.UUID) -> models.Bot:
        """Fetches and locks a bot model from database"""
        raise NotImplementedError()
