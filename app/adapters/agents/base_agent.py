import abc
import logging
import typing

from langchain_core.runnables import ConfigurableFieldSpec, RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from app import models, ports

logger = logging.getLogger(__name__)


class BaseLangChainAgent(ports.ChatBotAgent, abc.ABC):
    """
    Base class for all LangChain implementation of ChatbotAgent class.
    """

    def __init__(self, bot: models.Bot, **kwargs: typing.Any) -> None:
        self._model: ChatOpenAI | None = None
        self._chain: RunnableWithMessageHistory | None = None
        super().__init__(bot, **kwargs)

    @classmethod
    def _get_history_config(cls) -> list[ConfigurableFieldSpec]:
        return [
            ConfigurableFieldSpec(
                id="bot_id",
                annotation=str,
                name="Bot ID",
                description="Unique identifier for the bot.",
                default="",
                is_shared=True,
            ),
            ConfigurableFieldSpec(
                id="session_id",
                annotation=str,
                name="Session ID",
                description="Unique identifier for the session ID.",
                default="",
                is_shared=True,
            ),
        ]

    async def _invoke(self, session_id: str, message: str) -> typing.Any:
        if not self._chain:
            raise RuntimeError("Agent is not initialized")

        logger.info(
            "Invoking bot with session: %s and message: %s", session_id, message
        )
        config = typing.cast(
            RunnableConfig,
            {"configurable": {"session_id": session_id, "bot_id": str(self._bot.id)}},
        )

        response = await self._chain.ainvoke(
            {"input": message},
            config=config,
        )
        logger.info("Agent response: %s", response)

        return response

    def _stream(self, session_id: str, message: str) -> typing.Iterator[typing.Any]:
        if not self._chain:
            raise RuntimeError("Agent is not initialized")

        config = typing.cast(
            RunnableConfig,
            {"configurable": {"session_id": session_id, "bot_id": str(self._bot.id)}},
        )

        yield from self._chain.stream(
            {"input": message},
            config=config,
        )
