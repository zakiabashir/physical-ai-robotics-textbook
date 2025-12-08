"""
Retrieval service for RAG implementation
Based on RAG-DOCS implementation
"""

from typing import List, Dict, Optional, Any
from app.services.embedding_service import embedding_service
from app.services.qdrant_client import QdrantClient
from app.services.cache_service import cache_service, cached_result
from app.services.query_expansion_service import query_expansion_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant documents using embeddings"""

    def __init__(self):
        self.qdrant_client = QdrantClient()
        self.collection_name = settings.COLLECTION_NAME

    async def retrieve(self, query: str, limit: int = 5, score_threshold: float = 0.7,
                    use_expansion: bool = True, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query with caching and optional query expansion

        Args:
            query: The search query
            limit: Maximum number of documents to retrieve
            score_threshold: Minimum similarity score threshold
            use_expansion: Whether to use query expansion
            context: Optional context for query expansion

        Returns:
            List of retrieved documents with metadata
        """
        # Expand query with context if provided
        if context:
            expanded_query = query_expansion_service.expand_with_context(query, context)
            query = expanded_query

        # Check cache first
        cache_key_data = {
            "query": query,
            "limit": limit,
            "score_threshold": score_threshold,
            "use_expansion": use_expansion
        }
        cached_result = cache_service.get("retrieve", cache_key_data)
        if cached_result is not None:
            logger.debug(f"Using cached retrieval results for query: {query[:50]}...")
            return cached_result

        all_results = []
        queries_to_try = [query]

        # Generate query expansions if enabled
        if use_expansion:
            expansions = query_expansion_service.expand_query(query, max_expansions=3)
            # Add expansions (skip the first one as it's the original)
            queries_to_try.extend(expansions[1:])

        try:
            # Try each query variant
            for i, try_query in enumerate(queries_to_try):
                if len(all_results) >= limit:
                    break

                # Generate embedding for the query
                query_embedding = embedding_service.get_embedding(try_query)

                # Adjust limit for remaining results
                remaining_limit = limit - len(all_results)

                # Search for similar documents
                results = await self.qdrant_client.search_similar(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=remaining_limit * 2,  # Get more to filter duplicates
                    score_threshold=score_threshold,
                    with_payload=True
                )

                # Format and filter results
                seen_ids = set(doc["id"] for doc in all_results)
                for result in results:
                    if result["id"] not in seen_ids:
                        doc = {
                            "id": result["id"],
                            "score": result["score"],
                            "text": result["payload"].get("text", ""),
                            "source": result["payload"].get("source", ""),
                            "title": result["payload"].get("title", ""),
                            "url": result["payload"].get("url", ""),
                            "chunk_id": result["payload"].get("chunk_id", ""),
                            "metadata": result["payload"].get("metadata", {}),
                            "query_match": try_query  # Track which query matched
                        }
                        all_results.append(doc)
                        seen_ids.add(result["id"])

            # Sort by score and limit
            all_results.sort(key=lambda x: x["score"], reverse=True)
            all_results = all_results[:limit]

            # Cache the result
            cache_service.set("retrieve", all_results, cache_key_data, ttl=300)  # Cache for 5 minutes

            logger.info(f"Retrieved {len(all_results)} documents for {len(queries_to_try)} query variants: {query[:50]}...")
            return all_results

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    async def retrieve_with_reranking(self, query: str, limit: int = 5, score_threshold: float = 0.7,
                                      context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents with advanced reranking based on query type and relevance

        Args:
            query: The search query
            limit: Maximum number of documents
            score_threshold: Minimum similarity score
            context: Optional context

        Returns:
            List of reranked documents
        """
        # Get initial retrieval results
        initial_results = await self.retrieve(
            query=query,
            limit=limit * 2,  # Get more for reranking
            score_threshold=score_threshold * 0.8,  # Lower threshold for initial search
            use_expansion=True,
            context=context
        )

        if not initial_results:
            return []

        # Determine query type for specialized scoring
        query_type = query_expansion_service.get_query_type(query)
        key_terms = query_expansion_service.extract_key_terms(query)

        # Rerank based on query type and key terms
        reranked = []
        for doc in initial_results:
            score = doc["score"]
            text = doc["text"].lower()
            title = doc.get("title", "").lower()

            # Boost score for key term matches
            term_boost = 0
            for term in key_terms:
                if term in text:
                    term_boost += 0.1
                if term in title:
                    term_boost += 0.15

            # Query type-specific scoring
            type_boost = 0
            if query_type == "definition":
                if any(word in text for word in ["definition", "defined as", "refers to", "means"]):
                    type_boost = 0.2
            elif query_type == "howto":
                if any(word in text for word in ["step", "procedure", "method", "how to"]):
                    type_boost = 0.2
            elif query_type == "example":
                if any(word in text for word in ["example", "for instance", "such as", "like"]):
                    type_boost = 0.2

            # Combine scores
            final_score = score + term_boost + type_boost

            reranked.append({
                **doc,
                "rerank_score": final_score,
                "score_breakdown": {
                    "similarity": score,
                    "term_boost": term_boost,
                    "type_boost": type_boost
                }
            })

        # Sort by rerank score
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Return top results
        return reranked[:limit]

    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by its ID

        Args:
            doc_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        try:
            result = await self.qdrant_client.get_document_by_id(
                collection_name=self.collection_name,
                doc_id=doc_id
            )

            if result:
                return {
                    "id": result["id"],
                    "text": result["payload"].get("text", ""),
                    "source": result["payload"].get("source", ""),
                    "title": result["payload"].get("title", ""),
                    "url": result["payload"].get("url", ""),
                    "metadata": result["payload"].get("metadata", {})
                }

            return None

        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {str(e)}")
            return None

    async def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search documents by keyword in their text content

        Args:
            keyword: Keyword to search for
            limit: Maximum results

        Returns:
            List of matching documents
        """
        try:
            # Use the keyword as a query for semantic search
            return await self.retrieve(keyword, limit=limit, score_threshold=0.5)

        except Exception as e:
            logger.error(f"Error searching by keyword: {str(e)}")
            raise

    def format_retrieved_context(self, retrieved_docs: List[Dict[str, Any]], max_chars: int = 2000) -> str:
        """
        Format retrieved documents into context for LLM

        Args:
            retrieved_docs: List of retrieved documents
            max_chars: Maximum characters for the context

        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found in the textbook."

        context_parts = []
        current_length = 0

        for doc in retrieved_docs:
            # Format each document
            source_text = f"\nSource: {doc.get('source', 'Unknown')}"
            if doc.get('title'):
                source_text += f" - {doc['title']}"
            if doc.get('url'):
                source_text += f"\nURL: {doc['url']}"

            text_chunk = f"\n\n{doc['text']}{source_text}\n---"

            # Check if adding this would exceed the limit
            if current_length + len(text_chunk) > max_chars:
                break

            context_parts.append(text_chunk)
            current_length += len(text_chunk)

        # Combine all parts
        full_context = "Based on the Physical AI & Humanoid Robotics textbook:\n" + "".join(context_parts)

        # Truncate if still too long
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "..."

        return full_context


# Global instance
retrieval_service = RetrievalService()