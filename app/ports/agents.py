import abc
import typing

from app import models


class ChatBotAgent(abc.ABC):
    """
    Abstract class for agents
    """

    @abc.abstractmethod
    def initialize(self, bot: models.Bot) -> None:
        """Initializes the agent"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def invoke(self, session_id: str, message: str) -> str:
        """Runs the agent for a given message"""
        raise NotImplementedError()

    @abc.abstractmethod
    def stream(self, session_id: str, message: str) -> typing.Iterator[str]:
        """Streams the agent response for a given message"""
        raise NotImplementedError()
