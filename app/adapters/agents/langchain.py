import logging
import typing

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableFieldSpec, RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from app import models, ports
from app.adapters.agents import utils
from app.config import settings

logger = logging.getLogger(__name__)


class ChatBotAgent(ports.ChatBotAgent):
    """
    LangChain implementation of agent interface
    """

    def __init__(self) -> None:
        self._bot: models.Bot | None = None
        self._model = ChatOpenAI(
            model=settings.openai_model, openai_api_key=settings.openai_api_key  # type: ignore[call-arg]
        )
        self._chain: RunnableWithMessageHistory | None = None

    def initialize(self, bot: models.Bot) -> None:
        self._bot = bot
        # create prompts template based on the bot context
        context_messagess = [(ctx.role, ctx.content) for ctx in bot.contexts]
        prompt = ChatPromptTemplate.from_messages(
            [
                *context_messagess,
                MessagesPlaceholder(variable_name="message"),
            ]
        )
        chain = prompt | self._model
        with_message_history = RunnableWithMessageHistory(
            chain,  # type: ignore[arg-type]
            utils.get_session_history,
            history_factory_config=[
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
            ],
        )
        self._chain = with_message_history

    async def invoke(self, session_id: str, message: str) -> str:
        if not self._chain or not self._bot:
            raise RuntimeError("Agent is not initialized")

        logger.info(
            "Invoking bot with session: %s and message: %s", session_id, message
        )
        config = typing.cast(
            RunnableConfig,
            {"configurable": {"session_id": session_id, "bot_id": str(self._bot.id)}},
        )

        response = await self._chain.ainvoke(
            {"message": [HumanMessage(content=message)]},
            config=config,
        )

        return str(response.content)

    def stream(self, session_id: str, message: str) -> typing.Iterator[str]:
        if not self._chain or not self._bot:
            raise RuntimeError("Agent is not initialized")

        config = typing.cast(
            RunnableConfig,
            {"configurable": {"session_id": session_id, "bot_id": str(self._bot.id)}},
        )

        for response in self._chain.stream(
            {"message": [HumanMessage(content=message)]},
            config=config,
        ):
            yield str(response.content)
