import abc

from langchain_core.vectorstores import VectorStoreRetriever

from app import models


class VectorStore(abc.ABC):
    """
    Abstract class for vector stores.
    """

    @abc.abstractmethod
    async def index(self, bot: models.Bot) -> None:
        """
        Create a vector index for the given bot model
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_retriever(self, namespace: str) -> VectorStoreRetriever:
        """
        Get a vector retriever for the given namespace
        """
        raise NotImplementedError()
