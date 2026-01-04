"""Deterministic (non-LLM) grading implementations for Stage 3."""

import logging

from rag_core.schemas.models import GradingResult, RetrievalResult

logger = logging.getLogger(__name__)


class DeterministicRelevanceGrader:
    """
    Deterministic relevance grader using keyword overlap.

    Stage 3: Simple heuristic (no LLM calls)
    Stage 5: Replace with LLM-based RelevanceGrader
    """

    def __init__(self, threshold: float = 0.3):
        """
        Initialize grader.

        Args:
            threshold: Minimum keyword overlap ratio
        """
        self.threshold = threshold

    def grade(self, query: str, text: str) -> GradingResult:
        """
        Grade using keyword overlap.

        Simple heuristic:
        - Extract words from query
        - Count how many appear in text
        - Score = overlap_count / query_words

        Args:
            query: User query
            text: Text to grade

        Returns:
            Grading result
        """
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        overlap = query_words & text_words
        score = len(overlap) / len(query_words) if query_words else 0.0

        passed = score >= self.threshold

        return GradingResult(
            passed=passed,
            score=score,
            reason=(
                f"Keyword overlap: {len(overlap)}/{len(query_words)} words" if not passed else None
            ),
        )

    def grade_batch(self, query: str, results: list[RetrievalResult]) -> list[GradingResult]:
        """Grade multiple results."""
        return [self.grade(query, r.chunk.text) for r in results]

    def filter_relevant(
        self, query: str, results: list[RetrievalResult], threshold: float | None = None
    ) -> list[RetrievalResult]:
        """
        Filter results to only relevant chunks.

        Args:
            query: User query
            results: Retrieval results
            threshold: Override instance threshold

        Returns:
            Filtered results
        """
        thresh = threshold if threshold is not None else self.threshold
        grades = self.grade_batch(query, results)

        filtered = [
            result
            for result, grade in zip(results, grades, strict=True)
            if grade.passed and grade.score >= thresh
        ]

        logger.debug(f"Filtered {len(results)} → {len(filtered)} relevant chunks")
        return filtered


class DeterministicGroundednessGrader:
    """
    Deterministic groundedness grader using substring matching.

    Stage 3: Simple heuristic (no LLM calls)
    Stage 5: Replace with LLM-based GroundednessGrader
    """

    def __init__(self, min_substring_length: int = 10):
        """
        Initialize grader.

        Args:
            min_substring_length: Minimum matching substring length
        """
        self.min_substring_length = min_substring_length

    def grade(self, answer: str, context: list[RetrievalResult]) -> GradingResult:
        """
        Grade using substring matching.

        Simple heuristic:
        - Check if answer sentences appear in context
        - Score = matched_sentences / total_sentences

        Args:
            answer: Generated answer
            context: Retrieved chunks

        Returns:
            Grading result
        """
        # Concatenate context
        context_text = " ".join([r.chunk.text for r in context])

        # Split answer into sentences (simple split on .)
        sentences = [
            s.strip() for s in answer.split(".") if len(s.strip()) > self.min_substring_length
        ]

        if not sentences:
            return GradingResult(passed=True, score=1.0, reason="No sentences to check")

        # Count how many sentences have substantial overlap with context
        matched = 0
        for sentence in sentences:
            # Check if significant portion of sentence appears in context
            words = sentence.lower().split()
            if len(words) < 3:
                continue

            # Check for n-gram matches (simple heuristic)
            for i in range(len(words) - 2):
                trigram = " ".join(words[i : i + 3])
                if trigram in context_text.lower():
                    matched += 1
                    break

        score = matched / len(sentences) if sentences else 0.0
        passed = score >= 0.5  # At least 50% of sentences grounded

        return GradingResult(
            passed=passed,
            score=score,
            reason=f"Grounded sentences: {matched}/{len(sentences)}" if not passed else None,
        )
