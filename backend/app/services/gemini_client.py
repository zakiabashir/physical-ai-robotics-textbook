"""Google Gemini API Client for the Physical AI Textbook"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API"""

    def __init__(self):
        """Initialize Gemini client with API key"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model_name = "models/gemini-2.5-flash"
        self.embedding_model = "models/embedding-001"
        self.temperature = 0.7
        self.max_tokens = 4000

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Gemini

        Args:
            messages: List of chat messages with role and content
            context: Additional context for the conversation
            stream: Whether to stream the response

        Returns:
            Response dictionary with generated text and metadata
        """
        try:
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages(messages, context)

            # Create model instance
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                    "response_mime_type": "text/plain",
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            # Start a chat
            chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

            # Generate response
            response = chat.send_message(gemini_messages[-1] if gemini_messages else "Hello", stream=stream)

            if stream:
                # Handle streaming response
                content = ""
                for chunk in response:
                    content += chunk.text
                return {"content": content, "model": self.model_name}
            else:
                # Handle regular response
                content = response.text
                return {"content": content, "model": self.model_name}

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")

    def _convert_messages(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Convert OpenAI-style messages to Gemini format

        Args:
            messages: List of messages with role and content
            context: Additional context

        Returns:
            List of formatted messages for Gemini
        """
        gemini_messages = []

        # Add system prompt if provided in context
        if context and context.get("system_prompt"):
            gemini_messages.append(f"System: {context['system_prompt']}")

        # Add context information
        if context:
            context_parts = []
            if context.get("current_page"):
                context_parts.append(f"Current page: {context['current_page']}")
            if context.get("chapter_id"):
                context_parts.append(f"Chapter: {context['chapter_id']}")
            if context.get("lesson_id"):
                context_parts.append(f"Lesson: {context['lesson_id']}")

            if context_parts:
                gemini_messages.append(f"Context: {', '.join(context_parts)}")

        # Convert messages
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append(f"{role}: {msg['content']}")

        return gemini_messages

    async def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Embedding creation error: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")

    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                embedding = await self.create_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed text: {e}")
                # Return zero embedding as fallback
                embeddings.append([0.0] * 768)  # Gemini embedding dimension

        return embeddings

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code and provide explanation

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Analysis results
        """
        prompt = f"""
        Analyze this {language} code and provide:
        1. A brief explanation of what it does
        2. Key concepts demonstrated
        3. Any potential improvements
        4. How it relates to Physical AI and robotics

        Code:
        ```{language}
        {code}
        ```
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = await self.chat_completion(messages)
        return {
            "explanation": response["content"],
            "language": language,
            "concepts": [],
            "improvements": []
        }

    async def generate_quiz_question(
        self,
        topic: str,
        difficulty: str = "medium",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a quiz question based on topic

        Args:
            topic: Topic for the quiz question
            difficulty: Difficulty level
            context: Additional context

        Returns:
            Generated quiz question
        """
        prompt = f"""
        Generate a {difficulty} multiple-choice quiz question about {topic} in the context of Physical AI and robotics.

        Requirements:
        - Provide a clear question
        - Include 4 options (A, B, C, D)
        - Mark the correct answer
        - Provide a brief explanation
        {f'Use this context: {context}' if context else ''}

        Format as JSON:
        {{
            "question": "...",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct_answer": 0,
            "explanation": "..."
        }}
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.chat_completion(messages)
            # Try to parse JSON response
            return json.loads(response["content"])
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "question": "What is the main purpose of Physical AI?",
                "options": [
                    "A) To create virtual reality experiences",
                    "B) To integrate AI with physical systems and robots",
                    "C) To develop cloud-based AI services",
                    "D) To create purely software AI solutions"
                ],
                "correct_answer": 1,
                "explanation": "Physical AI focuses on integrating artificial intelligence with physical systems, enabling robots and machines to interact with the real world."
            }

    async def suggest_related_concepts(
        self,
        current_topic: str,
        user_level: str = "intermediate"
    ) -> List[str]:
        """
        Suggest related concepts for learning

        Args:
            current_topic: Current topic being studied
            user_level: User's proficiency level

        Returns:
            List of related concepts
        """
        prompt = f"""
        Suggest 5 related concepts for someone learning about {current_topic}.
        The user is at a {user_level} level.
        Focus on Physical AI and robotics applications.
        Return as a simple list.
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = await self.chat_completion(messages)
        concepts = response["content"].split('\n')
        return [c.strip().lstrip('- ').strip() for c in concepts if c.strip()][:5]

    async def code_completion(
        self,
        code: str,
        language: str,
        cursor_position: int
    ) -> Dict[str, Any]:
        """
        Provide code completion suggestions

        Args:
            code: Existing code
            language: Programming language
            cursor_position: Position of cursor in code

        Returns:
            Completion suggestions
        """
        prompt = f"""
        Complete this {language} code at the cursor position.
        Provide the most likely completion based on Physical AI/robotics context.

        Code:
        {code[:cursor_position]}[CURSOR]{code[cursor_position:]}
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = await self.chat_completion(messages)
        completion = response["content"].replace("[CURSOR]", "")

        return {
            "suggestion": completion,
            "confidence": 0.8
        }