import logging
import typing

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core import prompts
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import models, ports
from app.adapters.agents import utils
from app.config import settings

from .base_agent import BaseLangChainAgent

logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


class RAGAgent(BaseLangChainAgent):
    """
    LangChain RAG implementation of agent interface
    """

    def __init__(self, bot: models.Bot, vector_store: ports.VectorStore) -> None:
        self._vector_store = vector_store
        super().__init__(bot)

    def initialize(self) -> None:
        model_parms = self._bot.get_model_params()

        self._model = ChatOpenAI(
            openai_api_key=settings.openai_api_key,  # type: ignore[call-arg]
            **model_parms,
        )
        retriever = self._vector_store.get_retriever(namespace=str(self._bot.id))

        # contextualize question to include chat history
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                prompts.MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self._model, retriever, contextualize_q_prompt
        )

        # create prompts template based on the bot context
        context_messages = self._bot.get_context_prompts()
        prompt = prompts.ChatPromptTemplate.from_messages(
            [
                *context_messages,
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(self._model, prompt)
        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        # add chat memory
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            utils.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
            history_factory_config=self._get_history_config(),
        )
        self._chain = conversational_rag_chain

    async def invoke(self, session_id: str, message: str) -> str:
        response = await self._invoke(session_id, message)
        return str(response["answer"])

    def stream(self, session_id: str, message: str) -> typing.Iterator[str]:
        for chunk in self._stream(session_id, message):
            yield str(chunk["answer"])
