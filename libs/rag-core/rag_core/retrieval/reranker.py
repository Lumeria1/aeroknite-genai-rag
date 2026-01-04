"""Reranking strategies to refine retrieval results."""

import logging

from rag_core.schemas.models import RetrievalResult

logger = logging.getLogger(__name__)


class Reranker:
    """
    Rerank retrieval results using secondary criteria.

    Strategies:
    - Recency boost (favor newer documents)
    - Metadata boost (favor specific sources)
    - LLM-based reranking (Stage 5+)
    """

    def __init__(self, strategy: str = "none"):
        """
        Initialize reranker.

        Args:
            strategy: Reranking strategy ("none", "recency", "metadata")
        """
        self.strategy = strategy

    def rerank(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        """
        Rerank results based on strategy.

        Args:
            results: Initial retrieval results

        Returns:
            Reranked results (may have adjusted scores)
        """
        if self.strategy == "none" or not results:
            return results

        if self.strategy == "recency":
            return self._rerank_by_recency(results)

        logger.warning(f"Unknown reranking strategy: {self.strategy}")
        return results

    def _rerank_by_recency(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        """
        Boost scores for more recent chunks.

        Simple heuristic: boost = 1.0 for newest, 0.9 for oldest.
        """
        if not results:
            return results

        # Sort by creation date
        sorted_results = sorted(
            results,
            key=lambda r: r.chunk.created_at,
            reverse=True,  # Newest first
        )

        # Apply recency boost
        n = len(sorted_results)
        for i, result in enumerate(sorted_results):
            recency_factor = 1.0 - (i / n) * 0.1  # 1.0 → 0.9
            result.score *= recency_factor

        # Re-sort by adjusted score
        sorted_results.sort(key=lambda r: r.score, reverse=True)

        # Update ranks
        for rank, result in enumerate(sorted_results, start=1):
            result.rank = rank

        logger.debug(f"Reranked {len(results)} results by recency")
        return sorted_results
