"""Tests for the chat functionality"""

import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models.chat import ChatRequest, ChatResponse

client = TestClient(app)


@pytest.fixture
def mock_chatbot():
    """Mock chatbot for testing"""
    with patch('app.core.dependencies.get_chatbot') as mock:
        chatbot = AsyncMock()
        mock.return_value = chatbot
        yield chatbot


class TestChatEndpoints:
    """Test chat API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Physical AI" in data["message"]
        assert "version" in data

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    @pytest.mark.asyncio
    async def test_chat_message(self, mock_chatbot):
        """Test sending a chat message"""
        # Mock chatbot response
        mock_chatbot.process_message.return_value = {
            "message": "Test response",
            "sources": [],
            "related_concepts": ["test concept"],
            "code_examples": [],
            "suggestions": ["Learn more"],
            "can_explain_code": False,
            "related_content": []
        }

        response = client.post(
            "/api/v1/chat/",
            json={"message": "What is Physical AI?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Test response"
        assert "sources" in data
        assert "related_concepts" in data
        assert isinstance(data["related_concepts"], list)

    @pytest.mark.asyncio
    async def test_chat_message_with_context(self, mock_chatbot):
        """Test sending a chat message with context"""
        mock_chatbot.process_message.return_value = {
            "message": "Context-aware response",
            "sources": [{"title": "Chapter 1", "url": "/docs/chapter-1"}],
            "related_concepts": [],
            "code_examples": [],
            "suggestions": [],
            "can_explain_code": True,
            "related_content": []
        }

        response = client.post(
            "/api/v1/chat/",
            json={
                "message": "Explain this code",
                "context": {
                    "current_page": "/docs/chapter-1/lesson-1",
                    "lesson_id": "1",
                    "chapter_id": "1"
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["can_explain_code"] is True
        assert len(data["sources"]) > 0

    def test_chat_message_validation(self):
        """Test chat message validation"""
        # Test empty message
        response = client.post("/api/v1/chat/", json={"message": ""})
        assert response.status_code == 422

        # Test missing message
        response = client.post("/api/v1/chat/", json={})
        assert response.status_code == 422

        # Test message too long
        response = client.post(
            "/api/v1/chat/",
            json={"message": "a" * 1001}  # Over 1000 character limit
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_conversation_history(self, mock_chatbot):
        """Test retrieving conversation history"""
        mock_chatbot.get_conversation.return_value = {
            "conversation_id": "test-123",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00Z"},
                {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01Z"}
            ],
            "metadata": {}
        }

        response = client.get("/api/v1/chat/conversations/test-123")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 2

    @pytest.mark.asyncio
    async def test_feedback_submission(self, mock_chatbot):
        """Test submitting feedback"""
        mock_chatbot.submit_feedback.return_value = {"status": "success"}

        response = client.post(
            "/api/v1/chat/feedback",
            json={
                "conversation_id": "test-123",
                "message_id": "msg-456",
                "rating": 5,
                "comment": "Very helpful!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_feedback_validation(self):
        """Test feedback validation"""
        # Test invalid rating
        response = client.post(
            "/api/v1/chat/feedback",
            json={
                "conversation_id": "test",
                "message_id": "test",
                "rating": 6,  # Over 5
                "comment": "test"
            }
        )
        assert response.status_code == 422

        # Test missing required fields
        response = client.post(
            "/api/v1/chat/feedback",
            json={
                "conversation_id": "test"
                # Missing message_id and rating
            }
        )
        assert response.status_code == 422


class TestChatModels:
    """Test Pydantic models for chat"""

    def test_chat_request_model(self):
        """Test ChatRequest model validation"""
        # Valid request
        request = ChatRequest(message="Test message")
        assert request.message == "Test message"
        assert request.context is None
        assert request.conversation_id is None

        # Request with context
        request = ChatRequest(
            message="Test",
            context={"lesson_id": "1"},
            conversation_id="conv-123"
        )
        assert request.context["lesson_id"] == "1"
        assert request.conversation_id == "conv-123"

    def test_chat_response_model(self):
        """Test ChatResponse model validation"""
        response = ChatResponse(
            message="Test response",
            sources=[{"title": "Test", "url": "http://test.com"}],
            related_concepts=["concept1", "concept2"],
            code_examples=[{"code": "print('hello')", "language": "python"}],
            suggestions=["Learn more"],
            can_explain_code=True,
            related_content=[{"type": "lesson", "id": "1"}]
        )
        assert response.message == "Test response"
        assert len(response.sources) == 1
        assert response.can_explain_code is True
        assert len(response.related_concepts) == 2