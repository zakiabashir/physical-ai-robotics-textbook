"""Content parser for textbook MDX files"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentParser:
    """Parser for MDX textbook content"""

    def __init__(self):
        self.content_cache = {}
        self.sections_cache = {}

    def parse_mdx_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse an MDX file and extract content sections

        Args:
            file_path: Path to the MDX file

        Returns:
            Dictionary containing parsed content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
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

            # Extract sections
            sections = self._extract_sections(content_body)

            # Extract code blocks
            code_blocks = self._extract_code_blocks(content_body)

            # Extract diagrams/mermaid charts
            diagrams = self._extract_diagrams(content_body)

            # Extract key concepts
            key_concepts = self._extract_key_concepts(content_body)

            # Extract learning objectives
            learning_objectives = self._extract_learning_objectives(content_body)

            # Extract activities
            activities = self._extract_activities(content_body)

            # Extract quiz questions
            quiz_questions = self._extract_quiz_questions(content_body)

            return {
                "file_path": str(file_path),
                "frontmatter": frontmatter,
                "content": content_body,
                "sections": sections,
                "code_blocks": code_blocks,
                "diagrams": diagrams,
                "key_concepts": key_concepts,
                "learning_objectives": learning_objectives,
                "activities": activities,
                "quiz_questions": quiz_questions,
                "parsed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error parsing MDX file {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "content": "",
                "sections": [],
                "code_blocks": [],
                "diagrams": [],
                "key_concepts": [],
                "learning_objectives": [],
                "activities": [],
                "quiz_questions": [],
                "error": str(e)
            }

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections from content based on headers"""
        sections = []

        # Match markdown headers (# ## ### ####)
        header_pattern = r'^(#{1,4})\s+(.+)$'

        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            header_match = re.match(header_pattern, line)
            if header_match:
                # Save previous section
                if current_section:
                    current_section['content'] = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2)
                current_section = {
                    'level': level,
                    'title': title,
                    'content': []
                }
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            current_section['content'] = '\n'.join(current_content).strip()
            sections.append(current_section)

        return sections

    def _extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Extract code blocks from content"""
        code_blocks = []

        # Match code blocks with language specifier
        code_pattern = r'```(\w+)?\n(.*?)```'

        for match in re.finditer(code_pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2)

            code_blocks.append({
                'language': language,
                'code': code.strip(),
                'line_count': len(code.split('\n'))
            })

        return code_blocks

    def _extract_diagrams(self, content: str) -> List[Dict[str, Any]]:
        """Extract Mermaid diagrams from content"""
        diagrams = []

        # Match Mermaid diagram blocks
        mermaid_pattern = r'```mermaid\n(.*?)```'

        for match in re.finditer(mermaid_pattern, content, re.DOTALL):
            diagram_code = match.group(1)

            # Try to extract diagram type
            diagram_type_match = re.match(r'\s*(\w+)', diagram_code)
            diagram_type = diagram_type_match.group(1) if diagram_type_match else 'unknown'

            diagrams.append({
                'type': diagram_type,
                'code': diagram_code.strip()
            })

        return diagrams

    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content"""
        concepts = []

        # Look for bold text, emphasis, or concept markers
        bold_pattern = r'\*\*(.*?)\*\*'
        italic_pattern = r'\*(.*?)\*'
        concept_marker = r'Concept:\s*(.*?)(?:\n|$)'

        for match in re.finditer(bold_pattern, content):
            concepts.append(match.group(1))

        for match in re.finditer(italic_pattern, content):
            concepts.append(match.group(1))

        for match in re.finditer(concept_marker, content, re.IGNORECASE):
            concepts.append(match.group(1))

        # Remove duplicates and filter
        concepts = list(set(concepts))
        concepts = [c for c in concepts if len(c.strip()) > 2]

        return concepts[:20]  # Limit to top 20 concepts

    def _extract_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from content"""
        objectives = []

        # Look for learning objective sections
        lo_section_pattern = r'(?i)learning\s+objectives:(.*?)(?=\n#|\n\n[A-Z]|\Z)'

        for match in re.finditer(lo_section_pattern, content, re.DOTALL):
            section = match.group(1)

            # Extract list items or bullet points
            item_pattern = r'[-*]\s*(.*?)(?=\n[-*]|\n\n|$)'

            for item_match in re.finditer(item_pattern, section, re.DOTALL):
                objective = item_match.group(1).strip()
                if objective:
                    objectives.append(objective)

        return objectives

    def _extract_activities(self, content: str) -> List[Dict[str, Any]]:
        """Extract hands-on activities from content"""
        activities = []

        # Look for activity/lab sections
        activity_patterns = [
            r'(?i)(?:activity|lab|hands[-\s]?on):(.*?)(?=\n#|\n\n[A-Z]|\Z)',
            r'(?i)###\s*(?:activity|lab|hands[-\s]?on)(.*?)(?=\n#|\n\n[A-Z]|\Z)'
        ]

        for pattern in activity_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                activity_content = match.group(1).strip()

                # Try to extract title
                title_match = re.match(r'^(.*?)(?=\n)', activity_content)
                title = title_match.group(1) if title_match else "Activity"

                activities.append({
                    'title': title,
                    'content': activity_content,
                    'type': 'lab' if 'lab' in pattern.lower() else 'activity'
                })

        return activities[:5]  # Limit to 5 activities per file

    def _extract_quiz_questions(self, content: str) -> List[Dict[str, Any]]:
        """Extract quiz questions from content"""
        questions = []

        # Look for quiz sections
        quiz_patterns = [
            r'(?i)quiz:(.*?)(?=\n#|\n\n[A-Z]|\Z)',
            r'(?i)###\s*quiz(.*?)(?=\n#|\n\n[A-Z]|\Z)',
            r'(?i)\[\s*quiz\s*\](.*?)(?=\n#|\n\n[A-Z]|\Z)'
        ]

        for pattern in quiz_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                quiz_content = match.group(1).strip()

                # Extract questions (look for Q: or numbered items)
                q_pattern = r'(?:Q:\s*|(\d+\.)\s*)(.*?)(?=\n(?:A:|Q:|\d+\.|\n\n|$))'

                for q_match in re.finditer(q_pattern, quiz_content, re.DOTALL):
                    question_num = q_match.group(1) or "Q"
                    question_text = q_match.group(2).strip()

                    # Look for answer after the question
                    a_pattern = r'A:\s*(.*?)(?=\n(?:Q:|A:|\d+\.|\n\n|$))'
                    a_match = re.search(a_pattern, quiz_content[q_match.end():])

                    questions.append({
                        'number': question_num,
                        'question': question_text,
                        'answer': a_match.group(1).strip() if a_match else None,
                        'type': 'multiple_choice' if '?' in question_text else 'short_answer'
                    })

        return questions[:10]  # Limit to 10 questions per file

    def create_embeddings_text(self, parsed_content: Dict[str, Any]) -> List[str]:
        """
        Create text chunks for embedding from parsed content

        Args:
            parsed_content: Parsed content dictionary

        Returns:
            List of text chunks suitable for embedding
        """
        chunks = []
        file_path = parsed_content.get('file_path', 'unknown')

        # Add file path as context
        context_prefix = f"Source: {file_path}\n\n"

        # Add frontmatter if available
        if parsed_content.get('frontmatter'):
            frontmatter = parsed_content['frontmatter']
            if frontmatter.get('title'):
                chunks.append(f"{context_prefix}Title: {frontmatter['title']}")
            if frontmatter.get('description'):
                chunks.append(f"{context_prefix}Description: {frontmatter['description']}")

        # Add sections as chunks
        for section in parsed_content.get('sections', []):
            section_text = section.get('content', '').strip()
            if section_text and len(section_text) > 50:  # Only meaningful sections
                chunk = f"{context_prefix}Section: {section['title']}\n\n{section_text}"
                chunks.append(chunk)

        # Add learning objectives
        if parsed_content.get('learning_objectives'):
            objectives_text = '\n'.join(f"- {obj}" for obj in parsed_content['learning_objectives'])
            chunk = f"{context_prefix}Learning Objectives:\n\n{objectives_text}"
            chunks.append(chunk)

        # Add key concepts with context
        if parsed_content.get('key_concepts'):
            concepts_text = ', '.join(parsed_content['key_concepts'])
            chunk = f"{context_prefix}Key Concepts: {concepts_text}"
            chunks.append(chunk)

        # Process code blocks with explanations
        for code_block in parsed_content.get('code_blocks', []):
            code = code_block.get('code', '')
            if code and len(code) > 20:
                chunk = f"{context_prefix}Code Example ({code_block['language']}):\n\n```{code_block['language']}\n{code}\n```"
                chunks.append(chunk)

        return chunks

    def extract_lesson_metadata(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured metadata from parsed lesson content

        Args:
            parsed_content: Parsed content dictionary

        Returns:
            Structured metadata dictionary
        """
        frontmatter = parsed_content.get('frontmatter', {})

        # Extract lesson info from file path
        file_path = Path(parsed_content['file_path'])
        path_parts = file_path.parts

        # Try to extract chapter and lesson numbers
        chapter_match = None
        lesson_match = None

        for part in path_parts:
            if 'chapter' in part.lower():
                chapter_match = re.search(r'chapter[-_]?(\d+)', part.lower())
            elif 'lesson' in part.lower():
                lesson_match = re.search(r'lesson[-_]?(\d+)', part.lower())

        metadata = {
            'file_path': str(file_path),
            'chapter': int(chapter_match.group(1)) if chapter_match else None,
            'lesson': int(lesson_match.group(1)) if lesson_match else None,
            'title': frontmatter.get('title', ''),
            'description': frontmatter.get('description', ''),
            'difficulty': frontmatter.get('difficulty', 'intermediate'),
            'estimated_time': frontmatter.get('estimated_time', 30),
            'prerequisites': frontmatter.get('prerequisites', []),
            'learning_objectives': parsed_content.get('learning_objectives', []),
            'key_concepts': parsed_content.get('key_concepts', []),
            'has_code': len(parsed_content.get('code_blocks', [])) > 0,
            'has_diagrams': len(parsed_content.get('diagrams', [])) > 0,
            'has_activities': len(parsed_content.get('activities', [])) > 0,
            'has_quiz': len(parsed_content.get('quiz_questions', [])) > 0,
            'section_count': len(parsed_content.get('sections', [])),
            'code_languages': list(set(cb['language'] for cb in parsed_content.get('code_blocks', []))),
            'activity_count': len(parsed_content.get('activities', [])),
            'question_count': len(parsed_content.get('quiz_questions', [])),
            'parsed_at': parsed_content.get('parsed_at')
        }

        return metadata