"""
Embedding service using Cohere API
Based on RAG-DOCS implementation
"""

import cohere
from typing import List, Optional
import numpy as np
from app.services.cache_service import cache_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Cohere API"""

    def __init__(self):
        self.api_key = settings.COHERE_API_KEY
        self.model = settings.EMBED_MODEL
        self.client = cohere.Client(self.api_key)

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text with caching

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        # Check cache first
        cached = cache_service.get(text)
        if cached is not None:
            logger.debug(f"Using cached embedding for text: {text[:50]}...")
            return cached

        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                truncate="END"
            )
            embedding = response.embeddings[0]

            # Cache the embedding for frequently used queries
            # Only cache if text is not too long (common queries)
            if len(text) < 200:
                cache_service.set(text, embedding, ttl=3600)  # Cache for 1 hour

            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding lists
        """
        try:
            # Cohere API has a limit on texts per request
            batch_size = 96  # Safe limit for embed-english-v3.0
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    truncate="END"
                )
                all_embeddings.extend(response.embeddings)

            return all_embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to numpy arrays
            e1 = np.array(embedding1)
            e2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(e1, e2)
            norms = np.linalg.norm(e1) * np.linalg.norm(e2)

            if norms == 0:
                return 0.0

            similarity = dot_product / norms
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0


# Global instance
embedding_service = EmbeddingService()