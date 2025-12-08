"""Content router for serving textbook content"""

from fastapi import APIRouter, HTTPException, status, Path as FastAPIPath, Query
from typing import Dict, List, Any, Optional
import logging
import re
from pathlib import Path
import json
import yaml

logger = logging.getLogger(__name__)

router = APIRouter()

# Content cache
_content_cache = {}


@router.get("/chapters")
async def get_chapters() -> List[Dict[str, Any]]:
    """
    Get list of all chapters with their lessons

    Returns:
        List of chapters with lesson information
    """
    try:
        chapters = []
        docs_path = Path("docs")

        # Scan for chapter directories
        for chapter_dir in sorted(docs_path.glob("chapter-*")):
            chapter_match = chapter_dir.name.split("-")
            if len(chapter_match) > 1:
                chapter_num = int(chapter_match[1])

                # Get chapter info from README or first lesson
                chapter_info = await _get_chapter_info(chapter_dir, chapter_num)

                # Get all lessons in this chapter
                lessons = []
                for lesson_file in sorted(chapter_dir.glob("lesson-*.mdx")):
                    lesson_match = lesson_file.stem.split("-")
                    if len(lesson_match) > 1:
                        lesson_num = int(lesson_match[1])

                        # Parse lesson frontmatter
                        lesson_info = await _parse_lesson_frontmatter(lesson_file)
                        lesson_info.update({
                            "id": f"{chapter_num}-{lesson_num}",
                            "chapter": chapter_num,
                            "lesson": lesson_num,
                            "path": f"/{chapter_dir.name}/{lesson_file.name}",
                            "url": f"/docs/{chapter_dir.name}/{lesson_file.name}"
                        })
                        lessons.append(lesson_info)

                chapter_info["lessons"] = lessons
                chapters.append(chapter_info)

        return chapters

    except Exception as e:
        logger.error(f"Error getting chapters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/chapters/{chapter_number}")
async def get_chapter(
    chapter_number: int = FastAPIPath(..., ge=1, le=4)
) -> Dict[str, Any]:
    """
    Get a specific chapter with all its lessons

    Args:
        chapter_number: Chapter number

    Returns:
        Chapter information with all lessons
    """
    try:
        chapter_dir = Path(f"docs/chapter-{chapter_number}")

        if not chapter_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {chapter_number} not found"
            )

        # Get chapter info
        chapter_info = await _get_chapter_info(chapter_dir, chapter_number)

        # Get all lessons
        lessons = []
        for lesson_file in sorted(chapter_dir.glob("lesson-*.mdx")):
            lesson_match = lesson_file.stem.split("-")
            if len(lesson_match) > 1:
                lesson_num = int(lesson_match[1])

                lesson_info = await _parse_lesson_frontmatter(lesson_file)
                lesson_info.update({
                    "id": f"{chapter_number}-{lesson_num}",
                    "chapter": chapter_number,
                    "lesson": lesson_num,
                    "path": f"/{chapter_dir.name}/{lesson_file.name}",
                    "url": f"/docs/{chapter_dir.name}/{lesson_file.name}"
                })
                lessons.append(lesson_info)

        chapter_info["lessons"] = lessons
        return chapter_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chapter {chapter_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/lessons/{chapter_number}/{lesson_number}")
async def get_lesson(
    chapter_number: int = FastAPIPath(..., ge=1, le=4),
    lesson_number: int = FastAPIPath(..., ge=1)
) -> Dict[str, Any]:
    """
    Get a specific lesson's content

    Args:
        chapter_number: Chapter number
        lesson_number: Lesson number

    Returns:
        Full lesson content
    """
    try:
        lesson_path = Path(f"docs/chapter-{chapter_number}/lesson-{lesson_number}.mdx")

        if not lesson_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {chapter_number}-{lesson_number} not found"
            )

        # Check cache first
        cache_key = str(lesson_path)
        if cache_key in _content_cache:
            cached_content = _content_cache[cache_key]
            # Check if file is still fresh
            import os
            if cached_content.get("mtime") == os.path.getmtime(lesson_path):
                return cached_content["content"]

        # Read and parse the lesson
        with open(lesson_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter
        frontmatter_match = content.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
            except yaml.YAMLError:
                frontmatter = {}
            content_body = content[frontmatter_match.end():].lstrip()
        else:
            frontmatter = {}
            content_body = content

        # Prepare lesson data
        lesson_data = {
            "id": f"{chapter_number}-{lesson_number}",
            "chapter": chapter_number,
            "lesson": lesson_number,
            "title": frontmatter.get("title", f"Lesson {lesson_number}"),
            "description": frontmatter.get("description", ""),
            "difficulty": frontmatter.get("difficulty", "intermediate"),
            "estimated_time": frontmatter.get("estimated_time", 30),
            "prerequisites": frontmatter.get("prerequisites", []),
            "learning_objectives": frontmatter.get("learning_objectives", []),
            "frontmatter": frontmatter,
            "content": content_body,
            "path": f"/chapter-{chapter_number}/lesson-{lesson_number}.mdx",
            "url": f"/docs/chapter-{chapter_number}/lesson-{lesson_number}.mdx"
        }

        # Cache the content
        import os
        _content_cache[cache_key] = {
            "content": lesson_data,
            "mtime": os.path.getmtime(lesson_path)
        }

        return lesson_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lesson {chapter_number}-{lesson_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search")
async def search_content(
    query: str = Query(..., min_length=2),
    chapter: Optional[int] = Query(None, ge=1, le=4),
    lesson: Optional[int] = Query(None, ge=1),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict[str, Any]]:
    """
    Simple text search through lesson content

    Args:
        query: Search query
        chapter: Filter by chapter
        lesson: Filter by lesson
        limit: Maximum results

    Returns:
        List of matching content
    """
    try:
        results = []
        query_lower = query.lower()

        # Search through all lessons
        docs_path = Path("docs")
        search_dirs = []

        if chapter:
            chapter_dir = docs_path / f"chapter-{chapter}"
            if chapter_dir.exists():
                search_dirs.append(chapter_dir)
        else:
            search_dirs = [d for d in docs_path.glob("chapter-*") if d.is_dir()]

        for chapter_dir in search_dirs:
            chapter_match = chapter_dir.name.split("-")
            if len(chapter_match) <= 1:
                continue
            chapter_num = int(chapter_match[1])

            for lesson_file in chapter_dir.glob("lesson-*.mdx"):
                lesson_match = lesson_file.stem.split("-")
                if len(lesson_match) <= 1:
                    continue
                lesson_num = int(lesson_match[1])

                # Skip if lesson filter is specified
                if lesson and lesson_num != lesson:
                    continue

                # Read lesson content
                with open(lesson_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()

                # Simple text matching
                if query_lower in content:
                    # Extract snippet around match
                    index = content.find(query_lower)
                    start = max(0, index - 100)
                    end = min(len(content), index + 200)
                    snippet = content[start:end].replace('\n', ' ').strip()

                    results.append({
                        "chapter": chapter_num,
                        "lesson": lesson_num,
                        "title": f"Chapter {chapter_num}, Lesson {lesson_num}",
                        "snippet": f"...{snippet}...",
                        "relevance": 1.0,  # Simple match
                        "url": f"/docs/chapter-{chapter_num}/lesson-{lesson_num}.mdx"
                    })

                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break

        return results

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/navigation")
async def get_navigation_structure() -> Dict[str, Any]:
    """
    Get the full navigation structure for the textbook

    Returns:
        Nested structure of chapters and lessons
    """
    try:
        nav = {
            "title": "Physical AI & Humanoid Robotics",
            "chapters": []
        }

        docs_path = Path("docs")

        for chapter_dir in sorted(docs_path.glob("chapter-*")):
            chapter_match = chapter_dir.name.split("-")
            if len(chapter_match) <= 1:
                continue
            chapter_num = int(chapter_match[1])

            chapter_data = {
                "id": chapter_num,
                "title": f"Chapter {chapter_num}",
                "lessons": []
            }

            # Try to get chapter title from README
            readme_path = chapter_dir / "README.md"
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith("# "):
                            chapter_data["title"] = line[2:].strip()
                            break

            for lesson_file in sorted(chapter_dir.glob("lesson-*.mdx")):
                lesson_match = lesson_file.stem.split("-")
                if len(lesson_match) <= 1:
                    continue
                lesson_num = int(lesson_match[1])

                # Get lesson title from frontmatter
                title = f"Lesson {lesson_num}"
                with open(lesson_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip().strip('"')
                            break

                chapter_data["lessons"].append({
                    "id": lesson_num,
                    "title": title,
                    "url": f"/docs/chapter-{chapter_num}/lesson-{lesson_num}.mdx"
                })

            nav["chapters"].append(chapter_data)

        return nav

    except Exception as e:
        logger.error(f"Navigation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/progress/{user_id}")
async def get_user_progress(
    user_id: str = FastAPIPath(...)
) -> Dict[str, Any]:
    """
    Get user's learning progress through the textbook

    Args:
        user_id: User identifier

    Returns:
        Progress information
    """
    # This would typically query a database
    # For now, return a template
    return {
        "user_id": user_id,
        "overall_progress": 0.0,
        "chapters_completed": 0,
        "lessons_completed": 0,
        "total_chapters": 4,
        "total_lessons": 12,
        "chapter_progress": {},
        "lesson_progress": {},
        "achievements": [],
        "streak": 0
    }


# Helper functions
async def _get_chapter_info(chapter_dir: Path, chapter_num: int) -> Dict[str, Any]:
    """Extract chapter information"""
    chapter_info = {
        "id": chapter_num,
        "title": f"Chapter {chapter_num}",
        "description": "",
        "estimated_time": 0
    }

    # Try to read README for chapter info
    readme_path = chapter_dir / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                chapter_info["title"] = title_match.group(1)

    # Chapter titles mapping
    chapter_titles = {
        1: "Physical AI Foundations",
        2: "Core Robotics Systems",
        3: "AI-Robot Intelligence",
        4: "Humanoid Robotics Capstone"
    }

    chapter_info["title"] = chapter_titles.get(chapter_num, chapter_info["title"])
    return chapter_info


async def _parse_lesson_frontmatter(lesson_file: Path) -> Dict[str, Any]:
    """Parse lesson frontmatter for metadata"""
    frontmatter = {}

    try:
        with open(lesson_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            try:
                frontmatter = yaml.safe_load(frontmatter_text) or {}
            except yaml.YAMLError:
                frontmatter = {}

    except Exception as e:
        logger.error(f"Error parsing {lesson_file}: {e}")

    return frontmatter