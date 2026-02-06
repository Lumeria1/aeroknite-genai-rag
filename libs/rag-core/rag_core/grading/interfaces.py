"""Grading interfaces (protocols for Stage 5+ implementations)."""

from typing import Protocol

from rag_core.schemas.models import GradingResult, RetrievalResult


class RelevanceGraderProtocol(Protocol):
    """
    Protocol for relevance grading implementations.

    Stage 3: DeterministicRelevanceGrader (keyword overlap)
    Stage 5+: LLM-based RelevanceGrader (OpenAI)
    """

    def grade(self, query: str, text: str) -> GradingResult:
        """
        Grade relevance of text to query.

        Args:
            query: User query
            text: Text to grade

        Returns:
            Grading result with pass/fail + confidence
        """
        ...

    def grade_batch(self, query: str, results: list[RetrievalResult]) -> list[GradingResult]:
        """
        Grade multiple results.

        Args:
            query: User query
            results: Retrieval results to grade

        Returns:
            List of grading results
        """
        ...


class GroundednessGraderProtocol(Protocol):
    """
    Protocol for groundedness grading implementations.

    Stage 3: DeterministicGroundednessGrader (substring matching)
    Stage 5+: LLM-based GroundednessGrader (OpenAI)
    """

    def grade(self, answer: str, context: list[RetrievalResult]) -> GradingResult:
        """
        Grade if answer is grounded in context.

        Args:
            answer: Generated answer
            context: Retrieved chunks used to generate answer

        Returns:
            Grading result indicating if answer is grounded
        """
        ...
