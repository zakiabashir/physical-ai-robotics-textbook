"""Tests for the content serving functionality"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open, MagicMock
from app.main import app

client = TestClient(app)


class TestContentEndpoints:
    """Test content API endpoints"""

    @patch('builtins.open', new_callable=mock_open, read_data="""---
title: Chapter 1
description: Test chapter
---
# Chapter 1 Content
This is test content for chapter 1.
""")
    @patch('os.path.exists', return_value=True)
    @patch('os.listdir')
    def test_get_chapters(self, mock_listdir, mock_exists, mock_file):
        """Test getting all chapters"""
        # Mock directory structure
        mock_listdir.return_value = ['chapter-1', 'chapter-2']

        response = client.get("/api/v1/content/chapters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Should return chapters even without lessons
        if data:
            assert "id" in data[0]
            assert "title" in data[0]

    @patch('builtins.open', new_callable=mock_open, read_data="""---
title: Chapter 1
description: Introduction to Physical AI
---
# Chapter 1: Physical AI Foundations
Lesson content here...
""")
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_get_chapter_by_id(self, mock_listdir, mock_exists, mock_file):
        """Test getting a specific chapter"""
        # Mock chapter exists
        def exists_side_effect(path):
            return 'chapter-1' in path and 'docs' in path

        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ['lesson-1.mdx', 'lesson-2.mdx']

        response = client.get("/api/v1/content/chapters/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "title" in data

    def test_get_chapter_invalid_id(self):
        """Test getting chapter with invalid ID"""
        response = client.get("/api/v1/content/chapters/99")
        assert response.status_code == 404

    @patch('builtins.open', new_callable=mock_open, read_data="""---
title: Lesson 1
description: First lesson
learning_objectives:
  - Understand Physical AI
  - Learn basic concepts
---
# Lesson 1: Introduction
Lesson content with **bold** text.
""")
    @patch('os.path.exists')
    def test_get_lesson(self, mock_exists, mock_file):
        """Test getting a specific lesson"""
        # Mock lesson exists
        def exists_side_effect(path):
            return 'chapter-1' in path and 'lesson-1.mdx' in path

        mock_exists.side_effect = exists_side_effect

        response = client.get("/api/v1/content/lessons/1/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1-1"
        assert data["chapter"] == 1
        assert data["lesson"] == 1
        assert data["title"] == "Lesson 1"
        assert "content" in data
        assert "learning_objectives" in data

    def test_get_lesson_invalid_params(self):
        """Test getting lesson with invalid parameters"""
        # Invalid chapter number
        response = client.get("/api/v1/content/lessons/99/1")
        assert response.status_code == 404

        # Invalid lesson number
        response = client.get("/api/v1/content/lessons/1/99")
        assert response.status_code == 404

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_search_content(self, mock_file, mock_listdir, mock_exists):
        """Test content search functionality"""
        # Mock search through lessons
        def exists_side_effect(path):
            return 'chapter-1' in path and 'lesson-1.mdx' in path

        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ['lesson-1.mdx']
        mock_file.return_value.read.return_value = """
        # Physical AI Introduction
        Physical AI combines artificial intelligence with physical robotics systems.
        This lesson covers the fundamentals of embodied intelligence.
        """.lower()

        response = client.get("/api/v1/content/search?query=Physical%20AI")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if data:
            assert "chapter" in data[0]
            assert "lesson" in data[0]
            assert "snippet" in data[0]
            assert "relevance" in data[0]

    def test_search_validation(self):
        """Test search query validation"""
        # Empty query
        response = client.get("/api/v1/content/search?query=")
        assert response.status_code == 422

        # Query too short
        response = client.get("/api/v1/content/search?query=a")
        assert response.status_code == 422

    @patch('os.listdir')
    def test_get_navigation_structure(self, mock_listdir):
        """Test getting navigation structure"""
        # Mock chapter directories
        mock_listdir.return_value = ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-4']

        response = client.get("/api/v1/content/navigation")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "chapters" in data
        assert len(data["chapters"]) == 4

    def test_get_user_progress(self):
        """Test getting user progress (mock implementation)"""
        response = client.get("/api/v1/content/progress/user123")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["user_id"] == "user123"
        assert "overall_progress" in data
        assert "total_chapters" in data
        assert data["total_chapters"] == 4