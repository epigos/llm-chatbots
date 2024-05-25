import typing

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from langchain_core.embeddings import embeddings
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from app import db, exceptions, models, ports
from app.adapters import agents, aws, qdrant, sqlalchemy
from app.config import settings
from app.helpers import auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


async def get_db_session() -> typing.AsyncIterator[AsyncSession]:
    """dependency to create new database session"""
    async with db.async_db.session() as session:
        yield session


DBSession = typing.Annotated[AsyncSession, Depends(get_db_session)]


async def get_bot_repo(session: DBSession) -> ports.BotRepository:
    """dependency to create new bot repository"""
    return sqlalchemy.BotRepository(session)


BotRepository = typing.Annotated[ports.BotRepository, Depends(get_bot_repo)]


async def get_user_repo(session: DBSession) -> ports.UserRepository:
    """dependency to create new user repository"""
    return sqlalchemy.UserRepository(session)


UserRepository = typing.Annotated[ports.UserRepository, Depends(get_user_repo)]


def get_token(token: typing.Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Dependency to retrive token from request, decode it
    and return the username attached to the token
    """
    error_msg = "Could not validate credentials"
    try:
        payload = auth.decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise exceptions.AuthenticationError(error_msg)

        return str(username)
    except InvalidTokenError as exc:
        raise exceptions.AuthenticationError(error_msg) from exc


TokenUsername = typing.Annotated[str, Depends(get_token)]


async def get_current_user(
    token_username: TokenUsername, user_repo: UserRepository
) -> models.User:
    """
    Dependency to retrieve current user from database for a given token username
    """
    try:
        user = await user_repo.get_by_username(token_username)
        return user
    except exceptions.DoesNotExist as exc:
        raise exceptions.AuthenticationError("Invalid user credentials") from exc


CurrentUser = typing.Annotated[models.User, Depends(get_current_user)]


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
    """Dependency to create a new vector store"""
    return qdrant.VectorStore(embedding=embedding)


VectorStore = typing.Annotated[ports.VectorStore, Depends(get_vector_store)]


def get_file_storage() -> ports.FileStorage:
    """Dependency to get file storage instance"""
    return aws.FileStorage(bucket_name=settings.s3_uploads_bucket_name)


FileStorage = typing.Annotated[ports.FileStorage, Depends(get_file_storage)]
