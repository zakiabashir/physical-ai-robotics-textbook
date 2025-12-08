"""
Physical AI Chatbot Service with RAG implementation
Based on RAG-DOCS agent.py implementation
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re
from datetime import datetime
import uuid
import time

from app.services.gemini_client import GeminiClient
from app.services.qdrant_client import QdrantClient
from app.services.retrieval_service import retrieval_service
from app.services.analytics_service import rag_analytics
from app.core.config import settings
from app.models.chat import Conversation, Feedback
from app.utils.content_parser import ContentParser

logger = logging.getLogger(__name__)


class PhysicalAIChatbot:
    """AI-powered chatbot for Physical AI textbook"""

    def __init__(self):
        self.gemini = GeminiClient()
        self.qdrant = QdrantClient()
        self.content_parser = ContentParser()
        self.retrieval_service = retrieval_service

        # Conversation storage (in production, use a database)
        self.conversations: Dict[str, Conversation] = {}
        self.feedback_db: List[Feedback] = []

        # Content cache
        self.content_cache: Dict[str, Any] = {}

        # System prompt - Updated for RAG
        self.system_prompt = """
        You are an AI tutor for the Physical AI & Humanoid Robotics textbook.
        Your role is to help students learn about Physical AI and humanoid robotics.

        IMPORTANT: Use only the information provided in the retrieved context to answer questions.
        If the context doesn't contain enough information to answer the question, say:
        "I don't have enough information in the textbook to answer that question."

        Guidelines:
        - Always base your answers on the retrieved textbook content
        - Explain concepts clearly and at an appropriate level
        - Provide examples when available in the context
        - Be encouraging and supportive
        - Ask follow-up questions to check understanding
        - Cite sources from the textbook when possible
        """

        # Fallback prompt for when RAG is unavailable
        self.fallback_prompt = """
        You are an AI tutor for Physical AI & Humanoid Robotics.
        The retrieval system is currently unavailable.

        Guidelines:
        - Provide general knowledge about Physical AI and robotics
        - Be transparent about limitations
        - Suggest checking the textbook for specific information
        - Encourage students to try again later
        - Do not make up specific textbook content
        """

    async def initialize_with_content(self):
        """Initialize chatbot with textbook content"""
        logger.info("Initializing chatbot with textbook content...")

        try:
            # Parse all content
            await self.parse_all_content()

            # Create embeddings
            await self.create_embeddings()

            logger.info("Chatbot initialization complete")

        except Exception as e:
            logger.error(f"Error initializing chatbot: {e}")

    async def parse_all_content(self):
        """Parse all textbook content"""
        content_path = settings.CONTENT_PATH

        # Walk through all MDX files
        for mdx_file in content_path.rglob("**/*.mdx"):
            try:
                content = await self.content_parser.parse_mdx_file(mdx_file)
                self.content_cache[mdx_file.name] = content
                logger.debug(f"Parsed: {mdx_file.name}")

            except Exception as e:
                logger.error(f"Error parsing {mdx_file}: {e}")

    async def create_embeddings(self):
        """Create embeddings for all content"""
        logger.info("Creating embeddings...")

        all_content = []
        all_metadata = []

        # Collect all content chunks
        for file_path, content in self.content_cache.items():
            if file_path.endswith('.mdx'):
                # Extract meaningful content chunks
                chunks = self._extract_content_chunks(content, file_path)
                for chunk in chunks:
                    all_content.append(chunk['text'])
                    all_metadata.append(chunk['metadata'])

        # Create embeddings in batches
        embeddings = await self.gemini.create_embeddings_batch(all_content)

        # Store in Qdrant
        collection_name = "content"
        points = []

        for i, (text, metadata, embedding) in enumerate(zip(all_content, all_metadata, embeddings)):
            point_id = f"{metadata['file_path']}_{i}"

            points.append({
                "id": point_id,
                "vector": embedding,
                "payload": metadata
            })

        if points:
            await self.qdrant.upsert_vectors(collection_name, points)
            logger.info(f"Created {len(points)} embeddings")

    def _extract_content_chunks(self, content: Dict, file_path: str) -> List[Dict]:
        """Extract content chunks from parsed content"""
        chunks = []

        # Add title and description
        if content.get('title'):
            chunks.append({
                "text": content['title'],
                "metadata": {
                    "file_path": file_path,
                    "type": "title",
                    "lesson": content.get('lesson', ''),
                    "chapter": content.get('chapter', '')
                }
            })

        if content.get('description'):
            chunks.append({
                "text": content['description'],
                "metadata": {
                    "file_path": file_path,
                    "type": "description",
                    "lesson": content.get('lesson', ''),
                    "chapter": content.get('chapter', '')
                }
            })

        # Add learning objectives
        if content.get('learning_objectives'):
            obj_text = "Learning Objectives: " + " ".join(content['learning_objectives'])
            chunks.append({
                "text": obj_text,
                "metadata": {
                    "file_path": file_path,
                    "type": "learning_objectives",
                    "lesson": content.get('lesson', ''),
                    "chapter": content.get('chapter', '')
                }
            })

        # Add code examples
        for code_block in content.get('code_examples', []):
            code_text = self._extract_code_content(code_block.get('code', ''))
            if code_text:
                chunks.append({
                    "text": code_text,
                    "metadata": {
                        "file_path": file_path,
                        "type": "code_example",
                        "language": code_block.get('language', 'python'),
                        "lesson": content.get('lesson', ''),
                        "chapter": content.get('chapter', ''),
                        "code_id": code_block.get('id', '')
                    }
                })

        # Add main content
        if content.get('content'):
            # Split content into paragraphs
            paragraphs = content['content'].split('\n\n')
            for paragraph in paragraphs:
                if len(paragraph.strip()) > 50:  # Only meaningful paragraphs
                    chunks.append({
                        "text": paragraph,
                        "metadata": {
                            "file_path": file_path,
                            "type": "content",
                            "lesson": content.get('lesson', ''),
                            "chapter": content.get('chapter', '')
                        }
                    })

        return chunks

    def _extract_code_content(self, code_str: str) -> str:
        """Extract clean code content"""
        # Remove Python docstring indicators
        code_str = re.sub(r'"""[^"]*"""', '', code_str)
        code_str = re.sub(r"'''[^']*'''", '', code_str)

        # Remove comments
        lines = []
        for line in code_str.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(line)

        return '\n'.join(lines)

    async def process_message(
        self,
        message: str,
        context: Optional[Dict] = None,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response using RAG

        Args:
            message: User message
            context: Optional context about current page/selection
            conversation_id: Optional conversation ID
            user_id: Optional user ID for analytics

        Returns:
            Response dictionary with analytics tracking
        """
        # Track query start
        query_id = rag_analytics.track_query(message, conversation_id or "anonymous", user_id)
        start_time = time.time()

        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            conversation = self.conversations.get(conversation_id)
            if not conversation:
                conversation = Conversation(id=conversation_id)
                self.conversations[conversation_id] = conversation

            # Build conversation history
            history = self._get_conversation_history(conversation_id)

            # Retrieve relevant documents using RAG with fallback and timing
            retrieval_start = time.time()
            try:
                retrieved_docs = await self.retrieval_service.retrieve(
                    query=message,
                    limit=5,
                    score_threshold=0.7
                )
                rag_available = True
                rag_analytics.track_cache_hit(query_id, False)  # We'll refine this to check actual cache hit
            except Exception as e:
                logger.error(f"RAG retrieval failed: {str(e)}")
                retrieved_docs = []
                rag_available = False
                rag_analytics.track_error(query_id, "retrieval_error", str(e))
            finally:
                retrieval_time = time.time() - retrieval_start

            # Track retrieval metrics
            avg_score = sum(doc.get("score", 0) for doc in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0
            rag_analytics.track_retrieval(query_id, retrieval_time, len(retrieved_docs), avg_score)

            # Format retrieved context or use fallback
            if rag_available:
                if retrieved_docs:
                    rag_context = self.retrieval_service.format_retrieved_context(retrieved_docs)
                    use_fallback = False
                else:
                    rag_context = "No relevant information found in the textbook."
                    use_fallback = False
            else:
                # RAG system unavailable
                rag_context = "The textbook search system is currently unavailable."
                use_fallback = True

            # Add context if provided
            context_text = ""
            if context:
                context_text = self._build_context_text(context)

            # Build messages with appropriate system prompt
            system_prompt = self.fallback_prompt if use_fallback else self.system_prompt
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add RAG context
            messages.append({
                "role": "system",
                "content": f"Textbook Context:\n{rag_context}"
            })

            # Add current context if provided
            if context_text:
                messages.append({
                    "role": "system",
                    "content": f"Current Context: {context_text}"
                })

            # Add conversation history (last 10 messages)
            for msg in history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            # Generate response with timing
            generation_start = time.time()
            try:
                response = await self.gemini.chat_completion(
                    messages=messages,
                    max_tokens=settings.GEMINI_MAX_TOKENS,
                    temperature=settings.GEMINI_TEMPERATURE,
                    system_prompt=None  # Already included
                )
            except Exception as e:
                logger.error(f"Generation failed: {str(e)}")
                rag_analytics.track_error(query_id, "generation_error", str(e))
                raise
            finally:
                generation_time = time.time() - generation_start

            # Estimate token count (rough approximation)
            token_count = len(response.split()) * 1.3  # Rough estimate

            # Track generation
            rag_analytics.track_generation(query_id, generation_time, token_count, use_fallback)

            # Update conversation
            conversation.updated_at = datetime.utcnow()
            conversation.message_count += 1

            # Parse response for additional info
            parsed_response = self._parse_response(response)

            # Add sources if found
            if retrieved_docs:
                sources = self._format_rag_sources(retrieved_docs)
                parsed_response["sources"] = sources

                # Track potential source URLs for analytics
                for source in sources:
                    if source.get("url"):
                        rag_analytics.track_source_click(source["url"], query_id)

            # Add query ID for potential feedback tracking
            parsed_response["query_id"] = query_id
            parsed_response["response_time"] = time.time() - start_time

            return parsed_response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            rag_analytics.track_error(query_id, "processing_error", str(e))
            return {
                "message": "I apologize, but I encountered an error processing your message. Please try again.",
                "sources": [],
                "related_concepts": [],
                "code_examples": [],
                "suggestions": [],
                "query_id": query_id,
                "response_time": time.time() - start_time
            }

    def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []

        # Load history (in production, from database)
        # For now, return empty list
        return []

    def _build_context_text(self, context: Dict) -> str:
        """Build context text from context dict"""
        context_parts = []

        if context.get("lesson_id"):
            context_parts.append(f"Currently viewing lesson: {context['lesson_id']}")

        if context.get("section_title"):
            context_parts.append(f"Reading section: {context['section_title']}")

        if context.get("selected_text"):
            selected = context["selected_text"][:100]
            context_parts.append(f"Selected text: {selected_text}...")

        return " | ".join(context_parts)

    def _build_content_context(self, relevant_content: List[Dict]) -> str:
        """Build context from relevant content"""
        context_parts = []

        for item in relevant_content[:3]:  # Limit to 3 most relevant
            metadata = item.get("payload", {})
            if metadata.get("type") == "title":
                context_parts.append(f"Lesson: {metadata.get('lesson')} - {metadata.get('title', 'Unknown')}")
            elif metadata.get("type") == "concept":
                context_parts.append(f"Key concept: {metadata.get('concept', 'Unknown')}")

        return " | ".join(context_parts)

    def _format_sources(self, relevant_content: List[Dict]) -> List[Dict]:
        """Format sources for response"""
        sources = []

        for item in relevant_content[:5]:  # Limit to 5 sources
            metadata = item.get("payload", {})
            source = {
                "lesson": metadata.get("lesson"),
                "chapter": metadata.get("chapter"),
                "file_path": metadata.get("file_path"),
                "score": item.get("score", 0)
            }
            sources.append(source)

        return sources

    def _format_rag_sources(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """Format RAG sources for response"""
        sources = []

        for doc in retrieved_docs[:5]:  # Limit to 5 sources
            source = {
                "source": doc.get("source", "Unknown"),
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "score": doc.get("score", 0),
                "chunk_id": doc.get("chunk_id", "")
            }
            sources.append(source)

        return sources

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract additional info"""
        result = {
            "message": response,
            "sources": [],
            "related_concepts": self._extract_concepts(response),
            "code_examples": self._detect_code_examples(response),
            "suggestions": self._generate_suggestions(response)
        }

        # Check if response contains code that can be explained
        result["can_explain_code"] = bool(re.search(r"```[a-zA-Z]*", response))

        return result

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from response"""
        concepts = []

        # Physical AI related concepts
        physical_ai_concepts = [
            "embodied intelligence", "perception-action loop", "sensor fusion",
            "ros", "ros2", "gazebo", "unity", "urdf", "sdf",
            "kinematics", "dynamics", "control", "navigation", "manipulation",
            "humanoid robot", "biped locomotion", "balance", "zmp",
            "nvidia isaac", "vision-language-action", "vla", "conversational robot"
        ]

        text_lower = text.lower()
        for concept in physical_ai_concepts:
            if concept in text_lower:
                concepts.append(concept)

        return list(set(concepts))

    def _detect_code_examples(self, response: str) -> List[Dict[str, Any]]:
        """Detect code examples in response"""
        code_examples = []

        # Look for code blocks
        code_blocks = re.findall(r"```([a-zA-Z]*)\n(.*?)```", response, re.DOTALL)

        for match in code_blocks:
            language, code = match.groups()
            if len(code.strip()) > 20:  # Only meaningful code
                code_examples.append({
                    "language": language,
                    "code": code.strip(),
                    "line_count": len(code.split('\n'))
                })

        return code_examples

    def _generate_suggestions(self, response: str) -> List[str]:
        """Generate suggestions based on response"""
        suggestions = []

        # Common suggestions based on content
        if "kinematics" in response.lower():
            suggestions.extend([
                "Practice with the kinematics lab exercises",
                "Try the inverse kinematics examples"
            ])

        if "ros" in response.lower():
            suggestions.extend([
                "Install ROS 2 on your system",
                "Try running the ROS 2 examples"
            ])

        if "python" in response.lower():
            suggestions.extend([
                "Try running the code examples",
                "Experiment with the parameters"
            ])

        # Always suggest next steps
        suggestions.append("Ask a follow-up question for clarification")
        suggestions.append("Try the related quizzes")

        return suggestions[:3]  # Limit to 3 suggestions

    async def _search_relevant_content(
        self,
        query: str,
        context: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search for relevant content based on query"""
        try:
            # Create query embedding
            query_embedding = await self.gemini.create_embedding(query)

            # Search in content collection
            results = await self.qdrant.search_similar(
                collection_name="content",
                query_vector=query_embedding,
                limit=limit,
                score_threshold=0.6
            )

            return results

        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation history"""
        # In production, this would query a database
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []

        # Return mock data for now
        return []

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

    async def list_conversations(self, limit: int = 20) -> List[Dict]:
        """List all conversations"""
        # In production, this would query a database
        return []

    async def submit_feedback(
        self,
        conversation_id: str,
        message_id: str,
        rating: int,
        comment: str = "",
        category: str = "general"
    ) -> bool:
        """Submit feedback"""
        try:
            feedback = Feedback(
                conversation_id=conversation_id,
                message_id=message_id,
                rating=rating,
                comment=comment,
                category=category
            )

            self.feedback_db.append(feedback)
            logger.info(f"Feedback submitted: {rating}/5 - {category}")

            return True

        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return False

    async def ask_about_highlight(
        self,
        text: str,
        lesson_id: str,
        section: Optional[str] = None
    ) -> Dict[str, Any]:
        """Answer question about highlighted text"""
        # Search for relevant content
        query = f"What is {text} in lesson {lesson_id}"
        if section:
            query += f" section {section}"

        relevant_content = await self._search_relevant_content(query)

        # Build focused prompt
        prompt = f"""
        You are an expert Physical AI tutor.
        A student highlighted this text from lesson {lesson_id}:

        "{text}"

        Provide a clear explanation of what this text means in the context of Physical AI and Humanoid Robotics.
        """

        # Create simple context
        messages = [
            {
                "role": "system",
                "content": "You are an expert Physical AI tutor providing clear, educational explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Generate response
        response = await self.gemini.chat_completion(
            messages=messages,
            max_tokens=300,
            temperature=0.3
        )

        # Find related content
        related_content = await self._find_related_content(text, lesson_id)

        return {
            "response": response,
            "related_content": related_content,
            "can_explain_code": "```" in response
        }

    async def _find_related_content(self, text: str, lesson_id: str) -> List[Dict[str, Any]]:
        """Find content related to the highlighted text"""
        # Extract key terms from text
        terms = self._extract_key_terms(text)

        related = []

        for term in terms[:3]:  # Limit to 3 terms
            results = await self._search_relevant_content(
                f"{term} in lesson {lesson_id}",
                limit=2
            )
            related.extend(results)

        # Deduplicate by score
        unique_content = {}
        for item in related:
            key = item.get("payload", {}).get("id", "")
            if key not in unique_content or item["score"] > unique_content[key].get("score", 0):
                unique_content[key] = item

        # Sort by score and return top results
        sorted_content = sorted(
            unique_content.values(),
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        return sorted_content[:5]

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple term extraction (in production, use NLP)
        terms = []

        # Split by common delimiters
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "down", "out", "off", "over",
            "under", "above", "below", "between", "through", "during", "before",
            "after", "without", "within", "about", "into", "onto", "upon", "per",
            "via", "vs", "etc", "ie", "eg"
        }

        filtered_words = [w for w in words if w not in stop_words]

        # Keep longer words
        terms = [w for w in filtered_words if len(w) > 2]

        return list(set(terms))

    async def get_lesson_suggestions(self, lesson_id: str) -> List[str]:
        """Get contextual suggestions for a lesson"""
        suggestions = []

        # Get lesson content
        lesson_content = self.content_cache.get(f"chapter-1/lesson-1.mdx", {})
        if not lesson_content:
            return [
                "Read the introduction to understand the basics",
                "Complete the lab exercises for hands-on practice",
                "Take the quiz to test your understanding"
            ]

        # Generate suggestions based on lesson content
        if lesson_id == "lesson-1":
            suggestions = [
                "Try the perception-action loop lab exercise",
                "Read about real-world applications",
                "Explore the differences between digital and physical AI"
            ]
        elif lesson_id == "lesson-2":
            suggestions = [
                "Experiment with ROS 2 commands",
                "Create your first ROS 2 node",
                "Try the Gazebo simulation exercises"
            ]
        else:
            suggestions = [
                "Complete the lab exercises",
                "Review the key concepts",
                "Take the lesson quiz"
            ]

        return suggestions

    async def search_content(
        self,
        query: str,
        lesson_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search for content across the textbook"""
        all_results = []

        # Search in content collection
        try:
            query_embedding = await self.gemini.create_embedding(query)
            content_results = await self.qdrant.search_similar(
                collection_name="content",
                query_vector=query_embedding,
                limit=limit
            )

            # Filter by lesson if specified
            if lesson_id:
                filtered = []
                for result in content_results:
                    metadata = result.get("payload", {})
                    if metadata.get("lesson") == lesson_id:
                        filtered.append(result)
                content_results = filtered

            all_results.extend(content_results)

        except Exception as e:
            logger.error(f"Error searching content: {e}")

        return all_results