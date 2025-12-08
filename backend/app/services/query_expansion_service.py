"""
Query expansion service for better RAG retrieval
"""

import re
from typing import List, Set, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class QueryExpansionService:
    """Service for expanding queries to improve retrieval"""

    def __init__(self):
        # Physical AI domain-specific terms and their synonyms
        self.domain_synonyms = {
            # Core concepts
            "physical ai": ["embodied ai", "robotic ai", "ai in robotics"],
            "humanoid robot": ["humanoid", "biped robot", "android", "anthropomorphic robot"],
            "ros": ["robot operating system", "ros2", "robot os"],
            "gazebo": ["gazebo simulator", "robot simulation"],
            "perception": ["computer vision", "sensing", "visual perception"],
            "locomotion": ["walking", "gait", "movement", "mobility"],

            # Technical terms
            "kinematics": ["forward kinematics", "inverse kinematics", "joint movement"],
            "dynamics": ["robot dynamics", "force", "torque", "motion"],
            "control": ["feedback control", "pid control", "motion control"],
            "navigation": ["path planning", "slam", "localization", "mapping"],
            "manipulation": ["grasping", "pick and place", "arm control"],

            # AI/ML terms
            "machine learning": ["ml", "artificial intelligence", "neural networks"],
            "deep learning": ["deep neural networks", "dnn", "cnn", "rnn"],
            "reinforcement learning": ["rl", "q-learning", "policy gradient"],
            "computer vision": ["cv", "image processing", "object detection"],

            # Tools and frameworks
            "isaac": ["nvidia isaac", "isaac sim", "isaac gym"],
            "unity": ["unity3d", "unity robotics", "unity simulation"],
            "python": ["python3", "python programming"],
            "docker": ["containerization", "docker container"],

            # Physical AI applications
            "autonomous": ["autonomy", "self-driving", "automatic"],
            "embodiment": ["embodied intelligence", "physical embodiment"],
            "sensor": ["sensing", "detector", "perception sensor"],
            "actuator": ["motor", "actuation", "robotic actuator"],
        }

        # Acronyms and their expansions
        self.acronyms = {
            "ros": "robot operating system",
            "ros2": "robot operating system 2",
            "slam": "simultaneous localization and mapping",
            "rl": "reinforcement learning",
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "cv": "computer vision",
            "dnn": "deep neural network",
            "cnn": "convolutional neural network",
            "rnn": "recurrent neural network",
            "lstm": "long short-term memory",
            "gan": "generative adversarial network",
            "vae": "variational autoencoder",
            "pid": "proportional integral derivative",
            "imu": "inertial measurement unit",
            "lidar": "light detection and ranging",
            "rgb-d": "red green blue depth",
            "urdf": "unified robot description format",
            "sdf": "simulation description format",
        }

        # Common question patterns
        self.question_patterns = {
            "what is": ["definition", "explain", "describe", "meaning of"],
            "how does": ["process", "mechanism", "working", "operation"],
            "why is": ["reason", "purpose", "importance", "significance"],
            "where can": ["location", "place", "find", "get"],
            "how to": ["tutorial", "guide", "steps", "instructions"],
            "examples": ["example", "sample", "demonstration", "illustration"],
        }

    def expand_query(self, query: str, max_expansions: int = 5) -> List[str]:
        """
        Expand a query with synonyms and related terms

        Args:
            query: Original query
            max_expansions: Maximum number of expanded queries to return

        Returns:
            List of expanded queries including the original
        """
        expansions = [query.lower()]
        original_words = set(re.findall(r'\b\w+\b', query.lower()))

        # Generate synonym expansions
        for word in original_words:
            if word in self.domain_synonyms:
                for synonym in self.domain_synonyms[word]:
                    expanded = query.lower().replace(word, synonym)
                    if expanded not in expansions:
                        expansions.append(expanded)

        # Expand acronyms
        for word in original_words:
            if word in self.acronyms:
                expanded = query.lower().replace(word, self.acronyms[word])
                if expanded not in expansions:
                    expansions.append(expanded)

        # Add question pattern variations
        for pattern, alternatives in self.question_patterns.items():
            if pattern in query.lower():
                for alt in alternatives:
                    expanded = re.sub(pattern, alt, query.lower(), flags=re.IGNORECASE)
                    if expanded not in expansions:
                        expansions.append(expanded)

        # Limit number of expansions
        return expansions[:max_expansions]

    def extract_key_terms(self, query: str) -> List[str]:
        """
        Extract key domain terms from a query

        Args:
            query: The input query

        Returns:
            List of key terms found in the query
        """
        query_lower = query.lower()
        key_terms = []

        # Check for multi-word terms first
        multi_word_terms = [term for term in self.domain_synonyms.keys() if ' ' in term]
        for term in sorted(multi_word_terms, key=len, reverse=True):  # Check longer terms first
            if term in query_lower:
                key_terms.append(term)

        # Check for single-word terms
        words = re.findall(r'\b\w+\b', query_lower)
        for word in words:
            if word in self.domain_synonyms or word in self.acronyms:
                key_terms.append(word)

        return list(set(key_terms))

    def generate_related_queries(self, query: str, num_related: int = 3) -> List[str]:
        """
        Generate related queries based on domain knowledge

        Args:
            query: Original query
            num_related: Number of related queries to generate

        Returns:
            List of related queries
        """
        key_terms = self.extract_key_terms(query)
        related_queries = []

        # Generate queries based on key terms
        for term in key_terms[:3]:  # Limit to top 3 terms
            # What is X?
            related_queries.append(f"what is {term}")

            # How does X work?
            if term in ["ros", "gazebo", "isaac", "unity", "slam"]:
                related_queries.append(f"how does {term} work")

            # Examples of X
            related_queries.append(f"examples of {term}")

            # X tutorial/guide
            if term in ["kinematics", "dynamics", "control", "navigation"]:
                related_queries.append(f"{term} tutorial")

            # Advantages/disadvantages of X
            if term in ["physical ai", "humanoid robot", "ros", "gazebo"]:
                related_queries.append(f"advantages of {term}")
                related_queries.append(f"disadvantages of {term}")

        # Remove duplicates and limit
        related_queries = list(set(related_queries))
        return related_queries[:num_related]

    def expand_with_context(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Expand query with contextual information

        Args:
            query: Original query
            context: Context information (lesson, chapter, etc.)

        Returns:
            Expanded query with context
        """
        if not context:
            return query

        expanded_parts = [query]

        # Add lesson context
        if context.get("lesson_id"):
            lesson_id = context["lesson_id"]
            expanded_parts.append(f"lesson {lesson_id}")

        # Add chapter context
        if context.get("chapter_id"):
            chapter_id = context["chapter_id"]
            expanded_parts.append(f"chapter {chapter_id}")

        # Add section title
        if context.get("section_title"):
            section_title = context["section_title"]
            expanded_parts.append(f"section about {section_title}")

        # Add selected text if available
        if context.get("selected_text"):
            selected = context["selected_text"][:50]  # Limit to first 50 chars
            expanded_parts.append(f"related to {selected}")

        return " ".join(expanded_parts)

    def suggest_query_improvements(self, query: str) -> List[str]:
        """
        Suggest improvements to make a query more effective

        Args:
            query: The original query

        Returns:
            List of suggested improved queries
        """
        suggestions = []
        query_lower = query.lower()

        # Check if query is too short
        if len(query.split()) < 3:
            key_terms = self.extract_key_terms(query)
            if key_terms:
                suggestions.append(f"tell me more about {key_terms[0]}")
                suggestions.append(f"explain {key_terms[0]} in detail")

        # Check for ambiguous terms
        ambiguous_terms = {
            "robot": ["humanoid robot", "industrial robot", "mobile robot"],
            "ai": ["physical ai", "machine learning", "deep learning"],
            "control": ["feedback control", "motion control", "path control"],
            "simulation": ["gazebo simulation", "unity simulation", "isaac simulation"]
        }

        for word in re.findall(r'\b\w+\b', query_lower):
            if word in ambiguous_terms:
                for specific in ambiguous_terms[word]:
                    suggestions.append(query.lower().replace(word, specific))

        # Add "how to" for action-oriented queries
        if any(word in query_lower for word in ["make", "create", "build", "implement"]) and "how to" not in query_lower:
            suggestions.append(f"how to {query_lower}")

        # Remove duplicates and limit
        suggestions = list(set(suggestions))
        return suggestions[:5]

    def get_query_type(self, query: str) -> str:
        """
        Determine the type of query

        Args:
            query: The input query

        Returns:
            Query type: factual, howto, definition, comparison, example, other
        """
        query_lower = query.lower()

        # Check for definition queries
        if any(pattern in query_lower for pattern in ["what is", "define", "meaning of", "explain"]):
            return "definition"

        # Check for how-to queries
        if any(pattern in query_lower for pattern in ["how to", "how do", "how can", "steps to"]):
            return "howto"

        # Check for example queries
        if any(pattern in query_lower for pattern in ["example", "examples", "sample", "demonstration"]):
            return "example"

        # Check for comparison queries
        if any(pattern in query_lower for pattern in ["vs", "versus", "compare", "difference", "pros and cons"]):
            return "comparison"

        # Check for factual queries
        if any(pattern in query_lower for pattern in ["why is", "when was", "who created", "where can"]):
            return "factual"

        return "other"


# Global instance
query_expansion_service = QueryExpansionService()