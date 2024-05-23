from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain import document_loaders
from langchain_community import document_loaders
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app import models, typings
from app.adapters import qdrant


@pytest.fixture
@patch("qdrant_client.AsyncQdrantClient", autospec=True)
@patch("qdrant_client.QdrantClient", autospec=True)
def vector_store(mock_qdrant_client, mock_async_qdrant_client):
    embedding = mock.MagicMock(spec=Embeddings)
    return qdrant.VectorStore(embedding)


@pytest.mark.asyncio
@patch("langchain_qdrant.Qdrant.afrom_documents", new_callable=AsyncMock)
async def test_can_index_text_documents(
    mock_afrom_documents, vector_store, bot: models.Bot, bot_context: models.BotContext
):
    # Mock the asynchronous loading of documents
    bot.data_source = typings.BotDataSource.text
    bot.contexts = [bot_context]

    await vector_store.index(bot)

    # Check the Qdrant.afrom_documents is called
    mock_afrom_documents.assert_called_once()


@pytest.mark.asyncio
@patch("langchain_qdrant.Qdrant.afrom_documents", new_callable=AsyncMock)
async def test_can_index_uploaded_documents(
    mock_afrom_documents, vector_store, bot: models.Bot, bot_context: models.BotContext
):
    # Mock the asynchronous loading of documents
    bot.data_source = typings.BotDataSource.uploads
    bot.contexts = [bot_context]

    with patch.object(
        document_loaders.S3DirectoryLoader, "aload", new_callable=AsyncMock
    ) as mock_aload:
        mock_aload.return_value = [
            Document(page_content="test content", metadata={"title": "Test Document"})
        ]
        await vector_store.index(bot)

    mock_aload.assert_called_once()
    # Check the Qdrant.afrom_documents is called
    mock_afrom_documents.assert_called_once()


@pytest.mark.asyncio
@patch("langchain_qdrant.Qdrant.afrom_documents", new_callable=AsyncMock)
async def test_can_index_web_links(
    mock_afrom_documents, vector_store, bot: models.Bot, bot_context: models.BotContext
):
    # Mock the asynchronous loading of documents
    bot.data_source = typings.BotDataSource.web
    bot.contexts = [bot_context]

    with patch.object(
        document_loaders.WebBaseLoader, "aload", new_callable=MagicMock
    ) as mock_aload:
        mock_aload.return_value = [
            Document(page_content="test content", metadata={"title": "Test Document"})
        ]
        await vector_store.index(bot)

    mock_aload.assert_called_once()
    # Check the Qdrant.afrom_documents is called
    mock_afrom_documents.assert_called_once()


@patch("langchain_qdrant.Qdrant.as_retriever", autospec=True)
def test_get_retriever(mock_as_retriever, vector_store):
    namespace = "test_namespace"
    retriever = vector_store.get_retriever(namespace)

    # Ensure the retriever is returned correctly
    mock_as_retriever.assert_called_once_with(
        vector_store._store, search_kwargs={"filter": {"namespace": namespace}}
    )
    assert isinstance(
        retriever, MagicMock
    )  # assuming as_retriever returns a MagicMock in the mock setup
