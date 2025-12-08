"""
Comprehensive test suite for RAG functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.ingestion_service import IngestionService
from app.services.cache_service import CacheService
from app.core.config import settings


@pytest.fixture
def cache_service():
    """Create a test cache service"""
    return CacheService(default_ttl=1)


@pytest.fixture
def embedding_service():
    """Create a test embedding service"""
    return EmbeddingService()


@pytest.fixture
def retrieval_service():
    """Create a test retrieval service"""
    return RetrievalService()


@pytest.fixture
def ingestion_service():
    """Create a test ingestion service"""
    return IngestionService()


class TestCacheService:
    """Test the caching service"""

    def test_cache_set_and_get(self, cache_service):
        """Test basic cache set and get operations"""
        key = "test_key"
        value = {"test": "data"}

        cache_service.set(key, value)
        retrieved = cache_service.get(key)

        assert retrieved == value

    def test_cache_expiration(self, cache_service):
        """Test cache expiration"""
        key = "test_key"
        value = {"test": "data"}

        # Set with very short TTL
        cache_service.set(key, value, ttl=0.1)

        # Should be available immediately
        assert cache_service.get(key) == value

        # Wait for expiration
        asyncio.sleep(0.2)
        assert cache_service.get(key) is None

    def test_cache_max_size(self, cache_service):
        """Test cache max size eviction"""
        cache_service.max_size = 2

        # Add items up to max
        cache_service.set("key1", "value1")
        cache_service.set("key2", "value2")
        assert cache_service.get_stats()["size"] == 2

        # Add one more, should evict oldest
        cache_service.set("key3", "value3")
        assert cache_service.get_stats()["size"] == 2
        assert cache_service.get("key1") is None
        assert cache_service.get("key3") is not None

    def test_cache_clear(self, cache_service):
        """Test cache clearing"""
        cache_service.set("key1", "value1")
        cache_service.set("key2", "value2")
        assert cache_service.get_stats()["size"] == 2

        cache_service.clear()
        assert cache_service.get_stats()["size"] == 0


@pytest.mark.asyncio
class TestEmbeddingService:
    """Test the embedding service"""

    @patch('app.services.embedding_service.cohere.Client')
    async def test_get_embedding_success(self, mock_cohere, embedding_service):
        """Test successful embedding generation"""
        # Mock Cohere response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_client = Mock()
        mock_client.embed.return_value = mock_response
        mock_cohere.return_value = mock_client

        result = embedding_service.get_embedding("test text")
        assert result == [0.1, 0.2, 0.3]
        mock_client.embed.assert_called_once_with(
            texts=["test text"],
            model=settings.EMBED_MODEL,
            truncate="END"
        )

    @patch('app.services.embedding_service.cohere.Client')
    async def test_get_embedding_with_cache(self, mock_cohere, embedding_service):
        """Test embedding caching"""
        # Mock Cohere response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_client = Mock()
        mock_client.embed.return_value = mock_response
        mock_cohere.return_value = mock_client

        # First call should use API
        text = "short test"
        result1 = embedding_service.get_embedding(text)
        assert result1 == [0.1, 0.2, 0.3]
        assert mock_client.embed.call_count == 1

        # Second call should use cache
        result2 = embedding_service.get_embedding(text)
        assert result2 == result1
        assert mock_client.embed.call_count == 1  # Still only called once

    @patch('app.services.embedding_service.cohere.Client')
    async def test_get_embeddings_batch(self, mock_cohere, embedding_service):
        """Test batch embedding generation"""
        texts = ["text1", "text2", "text3"]
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

        # Mock Cohere response for batch
        mock_response = Mock()
        mock_response.embeddings = embeddings
        mock_client = Mock()
        mock_client.embed.return_value = mock_response
        mock_cohere.return_value = mock_client

        result = embedding_service.get_embeddings(texts)
        assert result == embeddings

    def test_calculate_similarity(self, embedding_service):
        """Test similarity calculation"""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        vec3 = [1, 0, 0]  # Same as vec1

        sim1 = embedding_service.calculate_similarity(vec1, vec2)
        sim2 = embedding_service.calculate_similarity(vec1, vec3)

        assert sim1 == 0.0  # Orthogonal vectors
        assert sim2 == 1.0  # Identical vectors


@pytest.mark.asyncio
class TestRetrievalService:
    """Test the retrieval service"""

    @patch('app.services.retrieval_service.QdrantClient')
    @patch('app.services.retrieval_service.embedding_service')
    async def test_retrieve_success(self, mock_embedding, mock_qdrant, retrieval_service):
        """Test successful document retrieval"""
        # Mock embedding
        mock_embedding.get_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock Qdrant response
        mock_results = [
            {
                "id": "doc1",
                "score": 0.9,
                "payload": {
                    "text": "Test document 1",
                    "source": "Test Source",
                    "title": "Test Title",
                    "url": "https://example.com",
                    "chunk_id": "0"
                }
            }
        ]
        mock_qdrant_client = AsyncMock()
        mock_qdrant_client.search_similar.return_value = mock_results
        mock_qdrant.return_value = mock_qdrant_client

        result = await retrieval_service.retrieve("test query")

        assert len(result) == 1
        assert result[0]["id"] == "doc1"
        assert result[0]["score"] == 0.9
        assert result[0]["text"] == "Test document 1"

    @patch('app.services.retrieval_service.QdrantClient')
    @patch('app.services.retrieval_service.embedding_service')
    async def test_retrieve_with_cache(self, mock_embedding, mock_qdrant, retrieval_service):
        """Test retrieval with caching"""
        # Mock embedding
        mock_embedding.get_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock Qdrant response
        mock_results = []
        mock_qdrant_client = AsyncMock()
        mock_qdrant_client.search_similar.return_value = mock_results
        mock_qdrant.return_value = mock_qdrant_client

        # First retrieval
        result1 = await retrieval_service.retrieve("test query", limit=5, score_threshold=0.7)
        assert result1 == []
        assert mock_qdrant_client.search_similar.call_count == 1

        # Second retrieval should use cache
        result2 = await retrieval_service.retrieve("test query", limit=5, score_threshold=0.7)
        assert result2 == result1
        assert mock_qdrant_client.search_similar.call_count == 1  # Still only called once

    def test_format_retrieved_context(self, retrieval_service):
        """Test context formatting"""
        docs = [
            {
                "text": "Document 1 content",
                "source": "Source 1",
                "title": "Title 1",
                "url": "https://example1.com"
            },
            {
                "text": "Document 2 content",
                "source": "Source 2",
                "title": "Title 2",
                "url": "https://example2.com"
            }
        ]

        context = retrieval_service.format_retrieved_context(docs)

        assert "Document 1 content" in context
        assert "Source 1" in context
        assert "Title 1" in context
        assert "https://example1.com" in context
        assert "Document 2 content" in context


@pytest.mark.asyncio
class TestIngestionService:
    """Test the ingestion service"""

    @patch('app.services.ingestion_service.requests.get')
    @patch('app.services.ingestion_service.trafilatura.fetch_url')
    @patch('app.services.ingestion_service.embedding_service')
    @patch('app.services.ingestion_service.QdrantClient')
    async def test_ingest_url_success(self, mock_qdrant, mock_embedding, mock_trafilatura, mock_requests, ingestion_service):
        """Test successful URL ingestion"""
        # Mock HTTP request
        mock_requests.return_value.text = "<html><body>Test content</body></html>"

        # Mock trafilatura
        mock_trafilatura.return_value = "Extracted text content"

        # Mock embedding
        mock_embedding.get_embeddings.return_value = [[0.1, 0.2, 0.3]]

        # Mock Qdrant
        mock_qdrant_client = AsyncMock()
        mock_qdrant.return_value = mock_qdrant_client

        result = await ingestion_service.ingest_url("https://example.com")

        assert result["success"] is True
        assert result["chunks_created"] > 0
        assert result["chunks_stored"] > 0
        assert result["error"] is None

    @patch('app.services.ingestion_service.requests.get')
    @patch('app.services.ingestion_service.trafilatura.fetch_url')
    async def test_extract_text_from_url(self, mock_trafilatura, mock_requests, ingestion_service):
        """Test text extraction from URL"""
        # Mock successful download
        mock_requests.return_value.status_code = 200
        mock_trafilatura.return_value = "Clean extracted text"
        mock_trafilatura.extract_title.return_value = "Test Title"

        result = ingestion_service.extract_text_from_url("https://example.com")

        assert result["text"] == "Clean extracted text"
        assert result["title"] == "Test Title"
        assert result["url"] == "https://example.com"
        assert result["error"] is None

    def test_chunk_text(self, ingestion_service):
        """Test text chunking"""
        text = "A" * 2500  # Long text
        title = "Test Title"
        url = "https://example.com"

        chunks = ingestion_service.chunk_text(text, title, url)

        assert len(chunks) > 1  # Should be split into multiple chunks
        assert all("text" in chunk for chunk in chunks)
        assert all(chunk["title"] == title for chunk in chunks)
        assert all(chunk["url"] == url for chunk in chunks)

    def test_get_source_name(self, ingestion_service):
        """Test source name extraction"""
        url1 = "https://example.com/path/to/document"
        url2 = "https://example.com/"
        url3 = "https://example.com/test-page-name"

        name1 = ingestion_service.get_source_name(url1)
        name2 = ingestion_service.get_source_name(url2)
        name3 = ingestion_service.get_source_name(url3)

        assert "example.com" in name1
        assert "document" in name1
        assert name2 == "example.com"
        assert "Test Page Name" in name3


@pytest.mark.asyncio
class TestRAGIntegration:
    """Integration tests for RAG pipeline"""

    @patch('app.services.ingestion_service.requests.get')
    @patch('app.services.ingestion_service.trafilatura.fetch_url')
    @patch('app.services.ingestion_service.embedding_service')
    @patch('app.services.ingestion_service.QdrantClient')
    @patch('app.services.retrieval_service.QdrantClient')
    async def test_end_to_end_rag(self, mock_retrieval_qdrant, mock_ingestion_qdrant,
                                   mock_embedding, mock_trafilatura, mock_requests):
        """Test complete RAG pipeline end-to-end"""
        # Setup mocks
        mock_requests.return_value.text = "<urlset><url><loc>https://example.com</loc></url></urlset>"
        mock_trafilatura.return_value = "Physical AI is the integration of AI in physical systems"
        mock_embedding.get_embeddings.return_value = [[0.1] * 1024]

        # Mock Qdrant for ingestion
        mock_ingestion_qdrant.return_value.get_collections.return_value.collections = []
        mock_ingestion_qdrant.return_value.create_collection.return_value = None
        mock_ingestion_qdrant.return_value.upsert_vectors.return_value = None

        # Mock Qdrant for retrieval
        mock_retrieval_results = [{
            "id": "doc1",
            "score": 0.9,
            "payload": {
                "text": "Physical AI is the integration of AI in physical systems",
                "source": "Example",
                "title": "Physical AI Introduction",
                "url": "https://example.com",
                "chunk_id": "0"
            }
        }]
        mock_retrieval_qdrant.return_value.search_similar.return_value = mock_retrieval_results

        # Test ingestion
        ingestion_service = IngestionService()
        ingestion_result = await ingestion_service.ingest_url("https://example.com")
        assert ingestion_result["success"] is True

        # Test retrieval
        retrieval_service = RetrievalService()
        retrieval_service.qdrant_client = mock_retrieval_qdrant.return_value
        retrieval_results = await retrieval_service.retrieve("What is Physical AI?")

        assert len(retrieval_results) == 1
        assert "Physical AI" in retrieval_results[0]["text"]
        assert retrieval_results[0]["score"] == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])