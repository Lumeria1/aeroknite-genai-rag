"""Metadata filtering utilities and ACL hooks."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MetadataFilter:
    """
    Build metadata filters for vector search.

    **IMPORTANT CONTRACT (Stage 3):**
    - Filters use JSONB containment operator (@>)
    - Only equality filters supported (e.g., {"category": "technical"})
    - Multi-value filters (OR logic) not yet supported
    - ACL hooks are placeholders (implementation in Stage 5+)

    Supports:
    - Equality filters (e.g., category="technical")
    - Single source filter
    - ACL hooks (future: user permissions)
    """

    @staticmethod
    def build_filters(
        category: str | None = None,
        source: str | None = None,
        sources: list[str] | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Build metadata filter dict for pgvector search.

        **Constraint**: Filters use JSONB @> (containment) operator.
        Multi-value OR logic (e.g., source IN [...]) requires SQL rewrite (Stage 5+).

        Args:
            category: Filter by category
            source: Filter by single source
            sources: Filter by list of sources (LIMITATION: uses first only)
            tags: Filter by tags (must contain all)
            user_id: Filter by ACL (future implementation)

        Returns:
            Metadata filter dict for PgVectorStore.similarity_search()

        Example:
            filters = MetadataFilter.build_filters(
                category="technical",
                source="manual.pdf",
            )
            # Returns: {"category": "technical", "source": "manual.pdf"}
        """
        filters: dict[str, Any] = {}

        if category:
            filters["category"] = category

        if source:
            filters["source"] = source
        elif sources:
            # LIMITATION: pgvector JSONB @> doesn't natively support OR queries
            # For now, we filter by first source only
            # Full multi-source filtering requires SQL OR logic (Stage 5+)
            filters["source"] = sources[0]
            if len(sources) > 1:
                logger.warning(
                    f"Multi-source filtering not yet supported (JSONB @> limitation). "
                    f"Using first source only: {sources[0]}. "
                    f"Full OR support requires SQL rewrite in Stage 5+."
                )

        if tags:
            # Check if metadata contains all tags
            filters["tags"] = tags

        if user_id:
            # Future: ACL implementation (Stage 5+)
            logger.info(f"ACL filtering for user {user_id} (not yet implemented)")

        return filters
