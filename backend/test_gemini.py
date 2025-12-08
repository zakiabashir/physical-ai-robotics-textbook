#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""

import os
import asyncio
from app.services.gemini_client import GeminiClient

async def test_gemini():
    """Test Gemini API functionality"""

    # Set your API key here or set as environment variable
    os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"

    try:
        # Initialize client
        client = GeminiClient()
        print("✅ Gemini client initialized successfully")

        # Test chat completion
        messages = [
            {"role": "user", "content": "What is Physical AI in one sentence?"}
        ]

        response = await client.chat_completion(messages)
        print(f"\n💬 Chat Response:")
        print(response["content"])

        # Test embedding
        text = "Physical AI combines artificial intelligence with physical systems"
        embedding = await client.create_embedding(text)
        print(f"\n📊 Embedding created successfully")
        print(f"Dimension: {len(embedding)}")

        # Test batch embeddings
        texts = [
            "Robotics is the study of robots",
            "Machine learning enables robots to learn",
            "Computer vision helps robots see"
        ]
        embeddings = await client.create_embeddings_batch(texts)
        print(f"\n📈 Batch embeddings created: {len(embeddings)} vectors")

        # Test code analysis
        code = """
        robot.move_forward(10)
        robot.turn_right(90)
        robot.move_forward(5)
        """
        analysis = await client.analyze_code(code, "python")
        print(f"\n🔍 Code Analysis:")
        print(analysis["explanation"][:200] + "...")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Set your GEMINI_API_KEY environment variable")
        print("2. Install required packages: pip install google-generativeai")

if __name__ == "__main__":
    asyncio.run(test_gemini())