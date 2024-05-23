import logging

import qdrant_client
from langchain_community import document_loaders
from langchain_core.documents import Document
from langchain_core.embeddings import embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_qdrant import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import models, ports, typings
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore(ports.VectorStore):
    """
    Qdrant implementation Vector Store class
    """

    def __init__(self, embedding: embeddings.Embeddings) -> None:
        self._embedding = embedding
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        self._sync_client = qdrant_client.QdrantClient(
            url=settings.qdrant_url, api_key=settings.qdrant_api_key, prefer_grpc=True
        )
        self._async_client = qdrant_client.AsyncQdrantClient(
            url=settings.qdrant_url, api_key=settings.qdrant_api_key, prefer_grpc=True
        )
        self._store = Qdrant(
            client=self._sync_client,
            collection_name=settings.qdrant_collection,
            embeddings=embedding,
            async_client=self._async_client,
        )

    @classmethod
    async def _load_documents(cls, bot: models.Bot) -> list[Document]:
        if bot.data_source == typings.BotDataSource.web:
            web_loader = document_loaders.WebBaseLoader(
                web_paths=[d.content for d in bot.documents],
            )
            docs = web_loader.aload()
        elif bot.data_source == typings.BotDataSource.uploads:
            s3_loader = document_loaders.S3DirectoryLoader(
                bucket=settings.s3_uploads_bucket_name,
                prefix=str(bot.id),
                region_name=settings.aws_default_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                endpoint_url=settings.aws_endpoint_url,
            )
            docs = await s3_loader.aload()
        else:
            docs = [
                Document(page_content=d.content, metadata=d.doc_metadata)
                for d in bot.documents
            ]

        for doc in docs:
            doc.metadata.update({"namespace": str(bot.id)})
        return docs

    async def index(self, bot: models.Bot) -> None:
        documents = await self._load_documents(bot)
        logger.info("Creating index for %s using documents: %s", bot, documents)

        splits = self._text_splitter.split_documents(documents)

        await Qdrant.afrom_documents(
            documents=splits,
            embedding=self._embedding,
            collection_name=settings.qdrant_collection,
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=True,
            force_recreate=settings.qdrant_recreate_collection,
        )
        logger.info("Document indexing successful")

    def get_retriever(self, namespace: str) -> VectorStoreRetriever:
        return self._store.as_retriever(
            search_kwargs={"filter": {"namespace": namespace}}
        )
