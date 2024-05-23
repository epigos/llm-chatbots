import typing

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from app.adapters.agents import utils
from app.config import settings

from .base_agent import BaseLangChainAgent


class ChatBotAgent(BaseLangChainAgent):
    """
    LangChain chatbot implementation of agent interface
    """

    def initialize(self) -> None:
        model_parms = self._bot.get_model_params()
        self._model = ChatOpenAI(
            openai_api_key=settings.openai_api_key,  # type: ignore[call-arg]
            **model_parms,
        )
        # create prompts template based on the bot context
        context_messagess = self._bot.get_context_prompts()
        prompt = ChatPromptTemplate.from_messages(
            [
                *context_messagess,
                MessagesPlaceholder(variable_name="input"),
            ]
        )
        chain = prompt | self._model
        with_message_history = RunnableWithMessageHistory(
            chain,  # type: ignore[arg-type]
            utils.get_session_history,
            input_messages_key="input",
            history_factory_config=self._get_history_config(),
        )
        self._chain = with_message_history

    async def invoke(self, session_id: str, message: str) -> str:
        resp = await self._invoke(session_id, message)
        return str(resp.content)

    def stream(self, session_id: str, message: str) -> typing.Iterator[str]:
        for chunk in self._stream(session_id, message):
            yield str(chunk.content)
