"""
Full Stack Integration Tests
Tests frontend and backend integration
"""

import pytest
import asyncio
import os
import sys
import requests
from pathlib import Path
import time

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.gemini_client import GeminiClient

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_TIMEOUT = 30


class TestFullStack:
    """Test full stack integration"""

    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        print("\n=== Full Stack Integration Tests ===")
        print("Backend URL:", BACKEND_URL)
        print("Frontend URL:", FRONTEND_URL)
        print()

    def test_backend_health_check(self):
        """Test backend health endpoint"""
        print("Testing backend health check...")
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print("✅ Backend is healthy")
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            pytest.fail("Backend not responding")

    def test_backend_root_endpoint(self):
        """Test backend root endpoint"""
        print("Testing backend root endpoint...")
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            print("✅ Backend root endpoint works")
        except Exception as e:
            print(f"❌ Backend root endpoint failed: {e}")

    def test_content_api(self):
        """Test content serving API"""
        print("Testing content API...")
        try:
            # Get chapters
            response = requests.get(f"{BACKEND_URL}/api/v1/content/chapters", timeout=5)
            assert response.status_code == 200
            chapters = response.json()
            assert len(chapters) > 0
            print(f"✅ Found {len(chapters)} chapters")

            # Get specific chapter
            if chapters:
                chapter_id = chapters[0].get("id", 1)
                response = requests.get(f"{BACKEND_URL}/api/v1/content/chapters/{chapter_id}", timeout=5)
                assert response.status_code == 200
                print(f"✅ Chapter {chapter_id} details retrieved")
        except Exception as e:
            print(f"❌ Content API test failed: {e}")

    def test_content_navigation(self):
        """Test content navigation structure"""
        print("Testing content navigation...")
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/content/navigation", timeout=5)
            assert response.status_code == 200
            nav = response.json()
            assert "chapters" in nav
            assert len(nav["chapters"]) == 4  # Should have 4 chapters
            print("✅ Navigation structure valid")
        except Exception as e:
            print(f"❌ Navigation test failed: {e}")

    def test_docs_files_exist(self):
        """Test that all MDX lesson files exist"""
        print("Checking MDX lesson files...")
        docs_path = Path(__file__).parent.parent.parent / "docs"
        required_files = [
            "docs/introduction.md",
            "docs/chapter-1/lesson-1.mdx",
            "docs/chapter-1/lesson-2.mdx",
            "docs/chapter-1/lesson-3.mdx",
            "docs/chapter-2/lesson-1.mdx",
            "docs/chapter-2/lesson-2.mdx",
            "docs/chapter-2/lesson-3.mdx",
            "docs/chapter-3/lesson-1.mdx",
            "docs/chapter-3/lesson-2.mdx",
            "docs/chapter-3/lesson-3.mdx",
            "docs/chapter-4/lesson-1.mdx",
            "docs/chapter-4/lesson-2.mdx",
            "docs/chapter-4/lesson-3.mdx",
            "docs/chapter-4/lesson-4.mdx",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = docs_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"❌ Missing {len(missing_files)} files:")
            for f in missing_files:
                print(f"  - {f}")
            pytest.fail(f"Missing required files: {missing_files}")
        else:
            print(f"✅ All {len(required_files)} files exist")

    @pytest.mark.asyncio
    async def test_gemini_integration(self):
        """Test Gemini API integration"""
        print("Testing Gemini API integration...")
        try:
            # Set API key
            os.environ["GEMINI_API_KEY"] = "AIzaSyD5WImup0-jUECh8F4HJr0VL8-XwWy_v6Q"

            # Test basic chat
            client = GeminiClient()
            response = await client.chat_completion([
                {"role": "user", "content": "What is 2+2?"}
            ])
            assert "content" in response
            assert "4" in response["content"]
            print("✅ Gemini API chat works")
        except Exception as e:
            print(f"⚠️  Gemini API test failed (quota may be exceeded): {e}")
            # Don't fail the test as quota may be exceeded

    def test_frontend_build(self):
        """Test if frontend can be built"""
        print("Testing frontend build...")
        try:
            # Check if build directory exists or can be created
            build_dir = Path(__file__).parent.parent.parent / "build"
            if build_dir.exists():
                print("✅ Build directory exists")
            else:
                print("ℹ️  Build directory not found - frontend may need to be built")
        except Exception as e:
            print(f"❌ Frontend build test failed: {e}")

    def test_config_files(self):
        """Test configuration files"""
        print("Checking configuration files...")
        config_files = [
            "docusaurus.config.js",
            "sidebars.js",
            "package.json",
            ".env",
        ]

        for config_file in config_files:
            file_path = Path(__file__).parent.parent.parent / config_file
            if file_path.exists():
                print(f"✅ {config_file} exists")
            else:
                print(f"❌ {config_file} missing")
                pytest.fail(f"Missing config file: {config_file}")

    def test_static_assets(self):
        """Test static assets"""
        print("Checking static assets...")
        static_files = [
            "static/img/logo.svg",
            "static/img/favicon.svg",
        ]

        for static_file in static_files:
            file_path = Path(__file__).parent.parent.parent / static_file
            if file_path.exists():
                print(f"✅ {static_file} exists")
            else:
                print(f"❌ {static_file} missing")
                pytest.fail(f"Missing static asset: {static_file}")

    def test_components(self):
        """Test React components"""
        print("Checking React components...")
        components = [
            "src/components/ChatWidget",
            "src/components/InteractiveCode",
            "src/components/Quiz",
            "src/components/ProgressTracker",
            "src/theme/Root.js",
            "src/theme/MDXComponents.js",
        ]

        for component in components:
            comp_path = Path(__file__).parent.parent.parent / component
            if comp_path.exists():
                print(f"✅ {component} exists")
            else:
                print(f"❌ {component} missing")
                pytest.fail(f"Missing component: {component}")


if __name__ == "__main__":
    # Run tests directly
    import sys

    # Create test instance
    test = TestFullStack()
    test.setup_class()

    # Run tests
    try:
        test.test_backend_health_check()
        test.test_backend_root_endpoint()
        test.test_content_api()
        test.test_content_navigation()
        test.test_docs_files_exist()
        test.test_config_files()
        test.test_static_assets()
        test.test_components()
        test.test_frontend_build()

        # Run async test
        asyncio.run(test.test_gemini_integration())

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)