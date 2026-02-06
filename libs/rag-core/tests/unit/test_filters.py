"""Test metadata filtering."""

import pytest
from rag_core.retrieval.filters import MetadataFilter


@pytest.mark.unit
def test_build_filters_single():
    """Test building single filter."""
    filters = MetadataFilter.build_filters(category="technical")
    assert filters == {"category": "technical"}


@pytest.mark.unit
def test_build_filters_multiple():
    """Test building multiple filters."""
    filters = MetadataFilter.build_filters(
        category="technical",
        source="manual.pdf",
    )
    assert filters == {"category": "technical", "source": "manual.pdf"}


@pytest.mark.unit
def test_build_filters_empty():
    """Test building empty filters."""
    filters = MetadataFilter.build_filters()
    assert filters == {}
