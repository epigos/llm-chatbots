import abc
import typing

from app import models


class ChatBotAgent(abc.ABC):
    """
    Abstract class for agents
    """

    def __init__(self, bot: models.Bot, **kwargs: typing.Any) -> None:
        self._bot = bot
        self._agent_kwargs = kwargs
        self.initialize()

    @abc.abstractmethod
    def initialize(self) -> None:
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


class BotAgentRepository(abc.ABC):
    """
    Abstract class for bot agent repositories
    """

    @abc.abstractmethod
    def get_agent(self, bot: models.Bot, **kwargs: typing.Any) -> ChatBotAgent:
        """
        Get agent for a given bot
        """
        raise NotImplementedError()
