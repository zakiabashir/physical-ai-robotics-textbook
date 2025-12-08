"""
Data ingestion service for RAG implementation
Based on RAG-DOCS main.py implementation
"""

import xml.etree.ElementTree as ET
import requests
import trafilatura
from typing import List, Dict, Optional, Any
import uuid
import logging
from urllib.parse import urljoin, urlparse
import time
import asyncio

from app.services.embedding_service import embedding_service
from app.services.qdrant_client import QdrantClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting web content into the vector database"""

    def __init__(self):
        self.qdrant_client = QdrantClient()
        self.sitemap_url = settings.SITEMAP_URL
        self.collection_name = settings.COLLECTION_NAME
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    async def get_all_urls(self) -> List[str]:
        """
        Extract all URLs from the sitemap

        Returns:
            List of URLs from the sitemap
        """
        try:
            logger.info(f"Fetching sitemap from: {self.sitemap_url}")
            response = requests.get(self.sitemap_url, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)
            urls = []

            # Extract URLs
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    urls.append(loc.text)

            logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls

        except Exception as e:
            logger.error(f"Error fetching sitemap: {str(e)}")
            raise

    def extract_text_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract clean text from a URL using trafilatura

        Args:
            url: URL to extract text from

        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            logger.info(f"Extracting text from: {url}")

            # Download and extract content
            downloaded = trafilatura.fetch_url(url)
            if downloaded is None:
                logger.warning(f"Could not download: {url}")
                return {"text": "", "title": "", "error": "Download failed"}

            # Extract content
            content = trafilatura.extract(downloaded, include_comments=False, include_formatting=False)
            title = trafilatura.extract_title(downloaded)

            if not content:
                logger.warning(f"No content extracted from: {url}")
                return {"text": "", "title": title or "", "error": "No content"}

            # Get metadata
            author = trafilatura.extract_author(downloaded)
            date = trafilatura.extract_date(downloaded)

            result = {
                "text": content,
                "title": title or "",
                "url": url,
                "author": author or "",
                "date": date or "",
                "error": None
            }

            logger.info(f"Extracted {len(content)} characters from: {url}")
            return result

        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return {"text": "", "title": "", "error": str(e)}

    def chunk_text(self, text: str, title: str = "", url: str = "") -> List[Dict[str, Any]]:
        """
        Split text into chunks

        Args:
            text: Text to chunk
            title: Document title
            url: Document URL

        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []

        chunks = []
        text_length = len(text)

        # Start from beginning of text
        start = 0
        chunk_id = 0

        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size

            # If this is the last chunk, take everything remaining
            if end >= text_length:
                chunk_text = text[start:]
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "title": title,
                    "url": url,
                    "start_pos": start,
                    "end_pos": text_length
                })
                break

            # Try to break at a sentence or paragraph
            chunk_text = text[start:end]

            # Look for sentence endings
            sentence_endings = ['. ', '! ', '? ', '\n\n']
            best_break = end

            for ending in sentence_endings:
                last_pos = chunk_text.rfind(ending)
                if last_pos > start + self.chunk_size // 2:  # At least half the chunk
                    best_break = start + last_pos + len(ending)
                    break

            # Create chunk
            chunk_text = text[start:best_break]
            chunks.append({
                "text": chunk_text,
                "chunk_id": chunk_id,
                "title": title,
                "url": url,
                "start_pos": start,
                "end_pos": best_break
            })

            # Move start position with overlap
            start = best_break - self.chunk_overlap
            if start < 0:
                start = 0

            chunk_id += 1

        logger.info(f"Created {len(chunks)} chunks from text ({text_length} chars)")
        return chunks

    async def embed(self, text_chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks

        Args:
            text_chunks: List of text chunks

        Returns:
            List of embeddings
        """
        try:
            logger.info(f"Generating embeddings for {len(text_chunks)} chunks")
            embeddings = embedding_service.get_embeddings(text_chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def save_chunk_to_qdrant(self, chunk: Dict[str, Any], embedding: List[float]):
        """
        Save a chunk with its embedding to Qdrant

        Args:
            chunk: Chunk dictionary with text and metadata
            embedding: Embedding vector
        """
        try:
            # Create point for Qdrant
            point_id = str(uuid.uuid4())

            payload = {
                "text": chunk["text"],
                "title": chunk["title"],
                "url": chunk["url"],
                "chunk_id": chunk["chunk_id"],
                "source": self.get_source_name(chunk["url"]),
                "metadata": {
                    "start_pos": chunk["start_pos"],
                    "end_pos": chunk["end_pos"],
                    "ingested_at": time.time()
                }
            }

            point = {
                "id": point_id,
                "vector": embedding,
                "payload": payload
            }

            # Save to Qdrant
            await self.qdrant_client.upsert_vectors(self.collection_name, [point])
            logger.debug(f"Saved chunk {chunk['chunk_id']} to Qdrant")

        except Exception as e:
            logger.error(f"Error saving chunk to Qdrant: {str(e)}")
            raise

    def get_source_name(self, url: str) -> str:
        """Extract a readable source name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            path = parsed.path.strip('/')

            if path:
                # Get last part of path
                parts = path.split('/')
                return f"{domain} - {parts[-1].replace('-', ' ').title()}"

            return domain

        except:
            return url

    async def ingest_url(self, url: str) -> Dict[str, Any]:
        """
        Ingest content from a single URL

        Args:
            url: URL to ingest

        Returns:
            Ingestion statistics
        """
        stats = {
            "url": url,
            "success": False,
            "chunks_created": 0,
            "chunks_embedded": 0,
            "chunks_stored": 0,
            "error": None
        }

        try:
            # Extract text
            content = self.extract_text_from_url(url)
            if content["error"] or not content["text"]:
                stats["error"] = content["error"] or "No content extracted"
                return stats

            # Create chunks
            chunks = self.chunk_text(content["text"], content["title"], url)
            if not chunks:
                stats["error"] = "No chunks created"
                return stats

            stats["chunks_created"] = len(chunks)

            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embed(texts)

            if len(embeddings) != len(chunks):
                stats["error"] = "Embedding count mismatch"
                return stats

            stats["chunks_embedded"] = len(embeddings)

            # Save chunks to Qdrant
            for chunk, embedding in zip(chunks, embeddings):
                await self.save_chunk_to_qdrant(chunk, embedding)
                stats["chunks_stored"] += 1

            stats["success"] = True
            logger.info(f"Successfully ingested {url}: {stats['chunks_stored']} chunks")
            return stats

        except Exception as e:
            stats["error"] = str(e)
            logger.error(f"Error ingesting {url}: {str(e)}")
            return stats

    async def ingest_book(self, max_urls: Optional[int] = None) -> Dict[str, Any]:
        """
        Ingest the entire book from the sitemap

        Args:
            max_urls: Maximum number of URLs to process (for testing)

        Returns:
            Overall ingestion statistics
        """
        stats = {
            "total_urls": 0,
            "successful_urls": 0,
            "failed_urls": 0,
            "total_chunks": 0,
            "start_time": time.time(),
            "errors": []
        }

        try:
            # Ensure collection exists
            await self.qdrant_client.create_collection(self.collection_name)

            # Get all URLs
            urls = await self.get_all_urls()

            if max_urls:
                urls = urls[:max_urls]
                logger.info(f"Limited to {max_urls} URLs for testing")

            stats["total_urls"] = len(urls)

            # Process each URL
            for i, url in enumerate(urls, 1):
                logger.info(f"Processing URL {i}/{len(urls)}: {url}")

                url_stats = await self.ingest_url(url)

                if url_stats["success"]:
                    stats["successful_urls"] += 1
                    stats["total_chunks"] += url_stats["chunks_stored"]
                else:
                    stats["failed_urls"] += 1
                    stats["errors"].append({
                        "url": url,
                        "error": url_stats["error"]
                    })

                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)

            stats["duration"] = time.time() - stats["start_time"]

            logger.info(f"Ingestion complete: {stats['successful_urls']}/{stats['total_urls']} URLs processed")
            logger.info(f"Total chunks stored: {stats['total_chunks']}")

            return stats

        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
            stats["errors"].append({"url": "global", "error": str(e)})
            return stats


# Global instance
ingestion_service = IngestionService()