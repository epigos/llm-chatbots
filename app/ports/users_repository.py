import abc
import uuid

from app import models


class UserRepository(abc.ABC):
    """
    Abstract class for user repositories.
    """

    @abc.abstractmethod
    async def save(self, user: models.User) -> models.User:
        """Save user model to database"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, user: models.User) -> None:
        """Deletes user model from database"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> models.User:
        """Returns user a single user model from database
        based on pk or raises 404 if not found"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_for_update(self, pk: uuid.UUID) -> models.User:
        """Fetches and locks a user model from database"""
        raise NotImplementedError()
