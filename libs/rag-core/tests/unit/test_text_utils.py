"""Test text processing utilities."""

import pytest
from rag_core.utils.text import clean_text


@pytest.mark.unit
def test_clean_text():
    """Test text cleaning (no dependencies)."""
    dirty = "  Hello\n\n\nworld  \n  "
    clean = clean_text(dirty)
    assert clean == "Hello\n\nworld"


@pytest.mark.unit
def test_clean_text_multiple_spaces():
    """Test multiple space removal."""
    text = "Hello    world"
    assert clean_text(text) == "Hello world"


# Token counting tests require tiktoken (Stage 5+ with [llm] extras)
# These tests are skipped in Stage 3 CI (hermetic requirement)


@pytest.mark.skip(reason="Requires tiktoken - install rag-core[llm] to enable")
@pytest.mark.unit
def test_count_tokens():
    """Test token counting (requires tiktoken)."""
    # Importing here (not at top) to allow test collection without tiktoken
    from rag_core.utils.text import count_tokens

    text = "Hello, world!"
    token_count = count_tokens(text)

    # Should be ~3-4 tokens
    assert 2 <= token_count <= 5


@pytest.mark.skip(reason="Requires tiktoken - install rag-core[llm] to enable")
@pytest.mark.unit
def test_truncate_text():
    """Test text truncation (requires tiktoken)."""
    from rag_core.utils.text import count_tokens, truncate_text

    text = "Hello " * 1000  # Very long text
    truncated = truncate_text(text, max_tokens=10)

    # Should be much shorter
    assert len(truncated) < len(text)
    assert count_tokens(truncated) <= 10
