"""
Qdrant vector database client for similarity search
Based on RAG-DOCS implementation
"""

from qdrant_client import QdrantClient as QdrantClientSDK
from qdrant_client.http import models as rest
from qdrant_client.models import Distance, VectorParams
from typing import List, Dict, Optional, Any, Union
import numpy as np
import logging
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantClient:
    """Qdrant client wrapper for vector operations"""

    def __init__(self):
        """Initialize Qdrant client"""
        self.client = QdrantClientSDK(
            url=settings.QDRANT_URL,
            api_key=getattr(settings, 'QDRANT_API_KEY', None)
        )
        self.url = settings.QDRANT_URL

    async def create_collection(self, collection_name: str):
        """Create a collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(
                c.name == collection_name for c in collections
            )

            if not exists:
                # Create collection with updated configuration
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.QDRANT_VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection {collection_name} already exists")

        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise

    async def upsert_vectors(self, collection_name: str, points: List[Dict]):
        """
        Upsert vectors into a collection

        Args:
            collection_name: Name of the collection
            points: List of point dictionaries with id, vector, and payload
        """
        try:
            # Convert points to Qdrant format
            qdrant_points = []
            for point in points:
                qdrant_points.append(
                    rest.PointStruct(
                        id=point["id"],
                        vector=point["vector"],
                        payload=point.get("payload", {})
                    )
                )

            # Upsert vectors
            operation_info = self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )

            logger.info(f"Upserted {len(points)} vectors to {collection_name}")

            return operation_info

        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise

    async def search_similar(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        limit: int = 10,
        score_threshold: float = 0.7,
        with_payload: bool = True
    ) -> List[Dict]:
        """
        Search for similar vectors

        Args:
            collection_name: Name of the collection
            query_vector: Query vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            with_payload: Whether to include payload in results

        Returns:
            List of similar documents
        """
        try:
            # Search in collection
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                score_threshold=score_threshold,
                with_payload=with_payload
            )

            # Format results
            results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            collections = self.client.get_collections().collections

            stats = {
                "collections": [c.name for c in collections],
                "total_documents": 0,
                "index_size": 0
            }

            for collection_name in stats["collections"]:
                try:
                    info = self.client.get_collection(collection_name)
                    stats["total_documents"] += info.vectors_count
                    stats["index_size"] += info.status.optimizer_info["segments_count"]
                except:
                    pass

            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "collections": [],
                "total_documents": 0,
                "index_size": 0
            }

    async def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")

        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            raise

    async def get_document_by_id(
        self,
        collection_name: str,
        doc_id: str
    ) -> Optional[Dict]:
        """Get a document by its ID"""
        try:
            # This would typically involve searching and filtering
            # Qdrant doesn't have a direct get by ID method
            results = await self.search_similar(
                collection_name=collection_name,
                query_vector=np.zeros(settings.VECTOR_SIZE),
                limit=1,
                with_payload=True
            )

            for result in results:
                if result["id"] == doc_id:
                    return result

            return None

        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None