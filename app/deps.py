import typing

from fastapi import Depends
from langchain_core.embeddings import embeddings
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from app import db, ports
from app.adapters import agents, qdrant, sqlalchemy
from app.config import settings


async def get_db_session() -> typing.AsyncIterator[AsyncSession]:
    """dependency to create new database session"""
    async with db.async_db.session() as session:
        yield session


DBSession = typing.Annotated[AsyncSession, Depends(get_db_session)]


async def get_bot_repo(session: DBSession) -> ports.BotRepository:
    """dependency to create new bot repository"""
    return sqlalchemy.BotRepository(session)


BotRepository = typing.Annotated[ports.BotRepository, Depends(get_bot_repo)]


async def get_bot_agent_repo() -> ports.BotAgentRepository:
    """Dependency to create new chatbot agent repository"""
    return agents.BotAgentRepository()


BotAgentRepository = typing.Annotated[
    ports.BotAgentRepository, Depends(get_bot_agent_repo)
]


def get_embeddings() -> embeddings.Embeddings:
    """Dependency to get LLM embeddings"""
    return OpenAIEmbeddings(openai_api_key=settings.openai_api_key)  # type: ignore[call-arg]


Embeddings = typing.Annotated[embeddings.Embeddings, Depends(get_embeddings)]


def get_vector_store(embedding: Embeddings) -> ports.VectorStore:
    """Dependency to a new vector store"""
    return qdrant.VectorStore(embedding=embedding)


VectorStore = typing.Annotated[ports.VectorStore, Depends(get_vector_store)]
