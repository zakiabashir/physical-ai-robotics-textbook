"""Embeddings router for content indexing and search"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json

from ..core.dependencies import get_chatbot
from ..services.chatbot import PhysicalAIChatbot
from ..models.chat import SearchResult, LessonSuggestion

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/index/content", status_code=status.HTTP_202_ACCEPTED)
async def index_textbook_content(
    collection_name: str = "textbook_content",
    rebuild: bool = False,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Index all textbook content into the vector database

    Args:
        collection_name: Name of the vector collection
        rebuild: Whether to rebuild the entire index

    Returns:
        Indexing status
    """
    try:
        logger.info(f"Starting content indexing for collection: {collection_name}")

        # Create collection if needed
        await chatbot.qdrant.create_collection(collection_name)

        # Parse and index content
        if rebuild:
            # Delete existing collection and recreate
            await chatbot.qdrant.delete_collection(collection_name)
            await chatbot.qdrant.create_collection(collection_name)

        # Get all MDX files
        docs_path = Path("docs")
        mdx_files = list(docs_path.glob("**/*.mdx"))

        if not mdx_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No MDX files found in docs directory"
            )

        indexed_count = 0
        errors = []

        for mdx_file in mdx_files:
            try:
                # Parse the file
                parsed = chatbot.content_parser.parse_mdx_file(mdx_file)

                # Create embedding chunks
                chunks = chatbot.content_parser.create_embeddings_text(parsed)

                # Create embeddings for chunks
                embeddings = await chatbot.openai.create_embeddings_batch(chunks)

                # Create points for Qdrant
                points = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    metadata = chatbot.content_parser.extract_lesson_metadata(parsed)

                    point = {
                        "id": f"{mdx_file.stem}_{i}",
                        "vector": embedding,
                        "payload": {
                            "text": chunk,
                            "file_path": str(mdx_file),
                            "chunk_index": i,
                            "metadata": metadata
                        }
                    }
                    points.append(point)

                # Batch upsert to Qdrant
                await chatbot.qdrant.upsert_vectors(collection_name, points)
                indexed_count += len(points)

            except Exception as e:
                error_msg = f"Error indexing {mdx_file}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        result = {
            "message": "Content indexing completed",
            "files_processed": len(mdx_files),
            "chunks_indexed": indexed_count,
            "errors": errors,
            "collection_name": collection_name
        }

        logger.info(f"Indexing complete: {indexed_count} chunks from {len(mdx_files)} files")
        return result

    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search")
async def search_content(
    query: str,
    collection_name: str = "textbook_content",
    limit: int = 10,
    score_threshold: float = 0.7,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
) -> List[SearchResult]:
    """
    Search for relevant content using semantic similarity

    Args:
        query: Search query
        collection_name: Vector collection to search
        limit: Maximum number of results
        score_threshold: Minimum similarity score

    Returns:
        List of search results
    """
    try:
        # Create query embedding
        query_embedding = await chatbot.openai.create_embedding(query)

        # Search in Qdrant
        results = await chatbot.qdrant.search_similar(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True
        )

        # Format results
        search_results = []
        for result in results:
            payload = result.get("payload", {})
            metadata = payload.get("metadata", {})

            search_result = SearchResult(
                lesson_id=metadata.get("lesson", "unknown"),
                chapter_id=f"chapter-{metadata.get('chapter', 'unknown')}",
                title=metadata.get("title", "Untitled"),
                content_snippet=payload.get("text", "")[:200] + "...",
                relevance_score=result.get("score", 0),
                url=f"/docs/{payload.get('file_path', '')}"
            )
            search_results.append(search_result)

        return search_results

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/suggest")
async def get_lesson_suggestions(
    lesson_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    concept: Optional[str] = None,
    limit: int = 5,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
) -> List[LessonSuggestion]:
    """
    Get personalized lesson suggestions based on user context

    Args:
        lesson_id: Current lesson ID
        difficulty: Preferred difficulty level
        concept: Specific concept to focus on
        limit: Maximum number of suggestions

    Returns:
        List of lesson suggestions
    """
    try:
        suggestions = []

        # Build search query based on context
        search_query = ""
        if concept:
            search_query = f"Explain {concept} in detail"
        elif lesson_id:
            search_query = f"Related content to lesson {lesson_id}"
        else:
            search_query = "Introduction to Physical AI concepts"

        # Search for related content
        query_embedding = await chatbot.openai.create_embedding(search_query)
        results = await chatbot.qdrant.search_similar(
            collection_name="textbook_content",
            query_vector=query_embedding,
            limit=limit * 2,  # Get more to filter
            score_threshold=0.6,
            with_payload=True
        )

        # Process and format suggestions
        seen_lessons = set()
        for result in results:
            payload = result.get("payload", {})
            metadata = payload.get("metadata", {})
            current_lesson_id = metadata.get("lesson", "unknown")

            # Skip if same lesson or already seen
            if current_lesson_id == lesson_id or current_lesson_id in seen_lessons:
                continue

            seen_lessons.add(current_lesson_id)

            # Determine suggestion type
            if metadata.get("has_activities"):
                suggestion_type = "practice"
            elif metadata.get("difficulty") == "beginner":
                suggestion_type = "theory"
            else:
                suggestion_type = "reference"

            # Create suggestion
            suggestion = LessonSuggestion(
                suggestion=f"Continue with: {metadata.get('title', 'Untitled Lesson')}",
                type=suggestion_type,
                priority=5 - int(result.get("score", 0) * 5),  # Convert score to priority
                related_lessons=[lesson_id] if lesson_id else []
            )
            suggestions.append(suggestion)

            if len(suggestions) >= limit:
                break

        return suggestions

    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/upload")
async def upload_and_index_file(
    file: UploadFile = File(...),
    collection_name: str = "textbook_content",
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Upload and index a single MDX file

    Args:
        file: MDX file to upload
        collection_name: Target vector collection

    Returns:
        Upload status
    """
    if not file.filename.endswith('.mdx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only MDX files are supported"
        )

    try:
        # Read file content
        content = await file.read()

        # Save to docs directory
        file_path = Path("docs") / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(content)

        # Parse and index the file
        parsed = chatbot.content_parser.parse_mdx_file(file_path)

        # Create embedding chunks
        chunks = chatbot.content_parser.create_embeddings_text(parsed)

        # Create embeddings
        embeddings = await chatbot.openai.create_embeddings_batch(chunks)

        # Create points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = chatbot.content_parser.extract_lesson_metadata(parsed)

            point = {
                "id": f"{file.filename}_{i}",
                "vector": embedding,
                "payload": {
                    "text": chunk,
                    "file_path": str(file_path),
                    "chunk_index": i,
                    "metadata": metadata
                }
            }
            points.append(point)

        # Upsert to Qdrant
        await chatbot.qdrant.upsert_vectors(collection_name, points)

        return {
            "message": "File uploaded and indexed successfully",
            "filename": file.filename,
            "chunks_indexed": len(chunks),
            "file_size": len(content)
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/collection/{collection_name}")
async def delete_collection(
    collection_name: str,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Delete a vector collection

    Args:
        collection_name: Name of collection to delete

    Returns:
        Deletion status
    """
    try:
        await chatbot.qdrant.delete_collection(collection_name)

        return {
            "message": f"Collection {collection_name} deleted successfully"
        }

    except Exception as e:
        logger.error(f"Collection deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/collections/stats")
async def get_collection_stats(
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Get statistics for all collections

    Returns:
        Collection statistics
    """
    try:
        stats = await chatbot.qdrant.get_collection_stats()
        return stats

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )