"""High-level retrieval interface."""

import logging
from typing import Any

from rag_core.schemas.models import RetrievalResult
from rag_core.stores.pgvector_store import PgVectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    High-level retrieval interface.

    Wraps PgVectorStore with additional business logic:
    - Default top_k and threshold settings
    - Automatic filtering
    - Logging and metrics hooks
    """

    def __init__(
        self,
        store: PgVectorStore,
        default_top_k: int = 5,
        default_threshold: float = 0.7,
    ):
        """
        Initialize retriever.

        Args:
            store: Vector store instance
            default_top_k: Default number of results
            default_threshold: Default similarity threshold
        """
        self.store = store
        self.default_top_k = default_top_k
        self.default_threshold = default_threshold

    def retrieve(
        self,
        query_embedding: list[float],
        top_k: int | None = None,
        threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks.

        Args:
            query_embedding: Query vector
            top_k: Number of results (uses default if None)
            threshold: Similarity threshold (uses default if None)
            filters: Metadata filters

        Returns:
            List of retrieval results, ranked by similarity
        """
        k = top_k if top_k is not None else self.default_top_k
        thresh = threshold if threshold is not None else self.default_threshold

        logger.info(f"Retrieving top-{k} chunks (threshold={thresh})")

        results = self.store.similarity_search(
            query_embedding=query_embedding,
            top_k=k,
            filters=filters,
            threshold=thresh,
        )

        logger.info(f"Retrieved {len(results)} chunks")
        return results
