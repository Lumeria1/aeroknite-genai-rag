"""Test Pydantic schema models."""

import pytest
from pydantic import ValidationError
from rag_core.schemas.models import Chunk, Citation, Document


@pytest.mark.unit
def test_chunk_model_valid():
    """Test valid chunk creation."""
    chunk = Chunk(
        document_id="doc_123",
        text="Example text",
        embedding=[0.1] * 1536,
        metadata={"source": "test.pdf"},
    )

    assert chunk.document_id == "doc_123"
    assert chunk.text == "Example text"
    assert len(chunk.embedding) == 1536
    assert chunk.id.startswith("chunk_")


@pytest.mark.unit
def test_chunk_model_invalid_embedding():
    """Test chunk with wrong embedding dimension."""
    with pytest.raises(ValidationError) as exc_info:
        Chunk(
            document_id="doc_123",
            text="Example",
            embedding=[0.1] * 100,  # Wrong dimension
        )

    assert "1536-dim embedding" in str(exc_info.value)


@pytest.mark.unit
def test_document_model():
    """Test document model."""
    doc = Document(
        title="Test Doc",
        source_uri="file:///test.pdf",
        metadata={"category": "test"},
    )

    assert doc.title == "Test Doc"
    assert doc.id.startswith("doc_")


@pytest.mark.unit
def test_citation_format():
    """Test citation formatting."""
    citation = Citation(
        chunk_id="chunk_123",
        document_id="doc_456",
        text="This is cited text from the document.",
        score=0.85,
        metadata={"source": "manual.pdf", "page": 5},
    )

    formatted = citation.format()
    assert "[manual.pdf, page 5]:" in formatted
    assert "This is cited text" in formatted
