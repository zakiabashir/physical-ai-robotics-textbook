"""Tests for the embeddings and search functionality"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import numpy as np
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_chatbot():
    """Mock chatbot for testing"""
    with patch('app.core.dependencies.get_chatbot') as mock:
        chatbot = AsyncMock()
        mock.return_value = chatbot
        yield chatbot


class TestEmbeddingsEndpoints:
    """Test embeddings API endpoints"""

    @pytest.mark.asyncio
    async def test_index_content(self, mock_chatbot):
        """Test content indexing endpoint"""
        # Mock successful indexing
        mock_chatbot.qdrant.create_collection.return_value = None
        mock_chatbot.qdrant.upsert_vectors.return_value = None
        mock_chatbot.content_parser.parse_mdx_file.return_value = {
            "sections": [{"title": "Test", "content": "Test content"}],
            "learning_objectives": ["Learn test"],
            "key_concepts": ["test concept"],
            "code_blocks": [{"code": "print('test')", "language": "python"}],
            "diagrams": [],
            "activities": [],
            "quiz_questions": []
        }
        mock_chatbot.content_parser.create_embeddings_text.return_value = [
            "Test content chunk 1",
            "Test content chunk 2"
        ]
        mock_chatbot.openai.create_embeddings_batch.return_value = [
            [0.1] * 1536,
            [0.2] * 1536
        ]

        response = client.post("/api/v1/embeddings/index/content")
        assert response.status_code == 202
        data = response.json()
        assert "files_processed" in data
        assert "chunks_indexed" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_search_content(self, mock_chatbot):
        """Test content search endpoint"""
        # Mock search results
        mock_chatbot.openai.create_embedding.return_value = [0.1] * 1536
        mock_chatbot.qdrant.search_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "payload": {
                    "text": "Physical AI is the integration of AI with physical systems",
                    "file_path": "docs/chapter-1/lesson-1.mdx",
                    "metadata": {
                        "lesson": 1,
                        "chapter": 1,
                        "title": "Introduction to Physical AI"
                    }
                }
            },
            {
                "id": "doc2",
                "score": 0.87,
                "payload": {
                    "text": "Embodied intelligence refers to AI that has a physical form",
                    "file_path": "docs/chapter-1/lesson-2.mdx",
                    "metadata": {
                        "lesson": 2,
                        "chapter": 1,
                        "title": "Embodied Intelligence"
                    }
                }
            }
        ]

        response = client.get("/api/v1/embeddings/search?query=Physical AI")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["relevance_score"] > data[1]["relevance_score"]
        assert "lesson_id" in data[0]
        assert "content_snippet" in data[0]

    @pytest.mark.asyncio
    async def test_get_lesson_suggestions(self, mock_chatbot):
        """Test lesson suggestions endpoint"""
        # Mock suggestions
        mock_chatbot.openai.create_embedding.return_value = [0.1] * 1536
        mock_chatbot.qdrant.search_similar.return_value = [
            {
                "id": "lesson2",
                "score": 0.9,
                "payload": {
                    "metadata": {
                        "lesson": 2,
                        "title": "Next Lesson",
                        "has_activities": True,
                        "difficulty": "intermediate"
                    }
                }
            }
        ]

        response = client.get(
            "/api/v1/embeddings/suggest?lesson_id=1&limit=3"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
        if data:
            assert "suggestion" in data[0]
            assert "type" in data[0]
            assert "priority" in data[0]

    @pytest.mark.asyncio
    async def test_upload_file(self, mock_chatbot):
        """Test file upload and indexing"""
        # Mock successful file processing
        mock_chatbot.content_parser.parse_mdx_file.return_value = {
            "sections": [],
            "learning_objectives": [],
            "key_concepts": [],
            "code_blocks": [],
            "diagrams": [],
            "activities": [],
            "quiz_questions": []
        }
        mock_chatbot.content_parser.create_embeddings_text.return_value = ["Test content"]
        mock_chatbot.openai.create_embeddings_batch.return_value = [[0.1] * 1536]
        mock_chatbot.qdrant.upsert_vectors.return_value = None

        # Create a test file
        test_content = b"""
---
title: Test Lesson
---
# Test Lesson

This is a test lesson content.
```python
print("Hello, World!")
```
        """

        files = {"file": ("test.mdx", test_content, "text/plain")}
        response = client.post(
            "/api/v1/embeddings/upload",
            files=files,
            data={"collection_name": "test_collection"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert data["filename"] == "test.mdx"
        assert "chunks_indexed" in data

    def test_upload_invalid_file_type(self):
        """Test uploading non-MDX file"""
        files = {"file": ("test.txt", b"Not an MDX file", "text/plain")}
        response = client.post("/api/v1/embeddings/upload", files=files)
        assert response.status_code == 400
        assert "Only MDX files" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_collection(self, mock_chatbot):
        """Test collection deletion"""
        mock_chatbot.qdrant.delete_collection.return_value = None

        response = client.delete("/api/v1/embeddings/collection/test_collection")
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, mock_chatbot):
        """Test collection statistics"""
        mock_chatbot.qdrant.get_collection_stats.return_value = {
            "collections": ["test_collection"],
            "total_documents": 100,
            "index_size": 5
        }

        response = client.get("/api/v1/embeddings/collections/stats")
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data
        assert data["total_documents"] == 100
        assert data["index_size"] == 5