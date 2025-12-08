"""
Simple test runner for RAG tests
"""

import sys
import os
import subprocess
import asyncio
import logging
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_command(cmd, description):
    """Run a command and log the result"""
    logger.info(f"Running: {description}")
    logger.info(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ {description} - SUCCESS")
        if result.stdout:
            logger.info(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - FAILED")
        logger.error(f"Error output:\n{e.stderr}")
        return False


async def run_rag_tests():
    """Run RAG-specific tests"""
    logger.info("Starting RAG Test Suite")
    logger.info("=" * 50)

    # Check if test dependencies are installed
    logger.info("\n1. Checking test dependencies...")
    if not run_command(
        [sys.executable, "-c", "import pytest; import pytest_asyncio"],
        "Test dependencies check"
    ):
        logger.error("Please install test dependencies: pip install pytest pytest-asyncio")
        return False

    # Run unit tests
    logger.info("\n2. Running unit tests...")
    test_file = Path(__file__).parent / "test_rag.py"
    if not run_command(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        "Unit tests"
    ):
        logger.error("Unit tests failed")
        return False

    # Run RAG health check
    logger.info("\n3. Running RAG health check...")
    try:
        from app.routers.health import detailed_health_check
        health_result = await detailed_health_check()

        if health_result.get("overall") == "healthy":
            logger.info("✅ RAG health check - PASSED")
        else:
            logger.warning("⚠️ RAG health check - DEGRADED")
            logger.info(f"Health status: {health_result}")
    except Exception as e:
        logger.error(f"❌ RAG health check - FAILED: {str(e)}")
        return False

    # Test RAG ingestion pipeline
    logger.info("\n4. Testing RAG ingestion pipeline...")
    try:
        from app.routers.health import test_ingestion_pipeline
        test_result = await test_ingestion_pipeline()

        if test_result.get("overall") == "passed":
            logger.info("✅ Ingestion pipeline test - PASSED")
        elif test_result.get("overall") == "partial":
            logger.warning("⚠️ Ingestion pipeline test - PARTIAL")
        else:
            logger.error("❌ Ingestion pipeline test - FAILED")
            logger.info(f"Test results: {test_result}")
    except Exception as e:
        logger.error(f"❌ Ingestion pipeline test - FAILED: {str(e)}")
        return False

    # Test cache functionality
    logger.info("\n5. Testing cache functionality...")
    try:
        from app.services.cache_service import cache_service

        # Test basic cache operations
        test_key = "test_key"
        test_value = {"test": "data"}

        cache_service.set(test_key, test_value)
        retrieved = cache_service.get(test_key)

        if retrieved == test_value:
            logger.info("✅ Cache functionality test - PASSED")
        else:
            logger.error("❌ Cache functionality test - FAILED")
            return False
    except Exception as e:
        logger.error(f"❌ Cache functionality test - FAILED: {str(e)}")
        return False

    # Test embedding service
    logger.info("\n6. Testing embedding service...")
    try:
        from app.services.embedding_service import embedding_service

        # This will make a real API call - make sure API key is set
        if settings.COHERE_API_KEY:
            test_embedding = embedding_service.get_embedding("test query")
            if test_embedding and len(test_embedding) > 0:
                logger.info(f"✅ Embedding service test - PASSED (dimension: {len(test_embedding)})")
            else:
                logger.error("❌ Embedding service test - FAILED: No embedding returned")
                return False
        else:
            logger.warning("⚠️ Skipping embedding test - COHERE_API_KEY not set")
    except Exception as e:
        logger.error(f"❌ Embedding service test - FAILED: {str(e)}")
        return False

    logger.info("\n" + "=" * 50)
    logger.info("🎉 All RAG tests completed successfully!")
    return True


def check_environment():
    """Check if the environment is properly configured"""
    logger.info("Checking environment configuration...")

    required_vars = [
        "GEMINI_API_KEY",
        "COHERE_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY"
    ]

    missing = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing.append(var)

    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.error("Please set these in your .env file")
        return False

    logger.info("✅ Environment configuration - OK")
    return True


async def main():
    """Main test runner"""
    logger.info("RAG Test Runner")
    logger.info("=" * 50)

    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Please configure your environment.")
        sys.exit(1)

    # Run tests
    success = await run_rag_tests()

    if success:
        logger.info("\n✅ All tests passed!")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())