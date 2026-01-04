"""Test vector similarity search end-to-end."""

import logging

import pytest
from rag_core.config import EMBEDDING_DIM
from rag_core.schemas.models import Chunk, Document
from rag_core.stores.pgvector_store import PgVectorStore

logger = logging.getLogger(__name__)


def _unit_vec(dim: int, idx: int) -> list[float]:
    v = [0.0] * dim
    v[idx] = 1.0
    return v


@pytest.mark.integration
def test_document_crud(vector_store: PgVectorStore):
    """Test document CRUD operations."""
    # Create
    doc = Document(
        id="test_doc_001",
        title="Test Document",
        source_uri="test://doc",
        content="None",
        metadata={"category": "test"},
    )
    vector_store.upsert_document(doc)

    # Read
    retrieved = vector_store.get_document("test_doc_001")
    assert retrieved is not None
    assert retrieved.title == "Test Document"

    # Delete
    deleted = vector_store.delete_document("test_doc_001")
    assert deleted is True

    # Verify deleted
    assert vector_store.get_document("test_doc_001") is None


@pytest.mark.integration
def test_chunk_crud(vector_store: PgVectorStore):
    """Test chunk CRUD operations."""
    # Setup: Create document first
    doc = Document(id="test_doc_002", title="Doc", source_uri="test://", content="None")
    vector_store.upsert_document(doc)

    # Create chunk
    chunk = Chunk(
        id="test_chunk_001",
        document_id="test_doc_002",
        text="Test chunk text",
        embedding=[0.1] * EMBEDDING_DIM,
        metadata={"test": True},
        chunk_index=0,
        start_char=None,
        end_char=None,
    )
    vector_store.upsert_chunk(chunk)

    # Read
    retrieved = vector_store.get_chunk("test_chunk_001")
    assert retrieved is not None
    assert retrieved.text == "Test chunk text"
    assert len(retrieved.embedding) == EMBEDDING_DIM


@pytest.mark.integration
def test_similarity_search(vector_store: PgVectorStore):
    doc = Document(id="test_doc_003", title="Doc", source_uri="test://", content=None)
    vector_store.upsert_document(doc)

    # Create 3 chunks with clearly different directions (cosine can distinguish)
    chunks = [
        Chunk(
            id="chunk_0",
            document_id="test_doc_003",
            text="Chunk 0",
            embedding=_unit_vec(EMBEDDING_DIM, 0),
            metadata={"index": 0},
            chunk_index=0,
            start_char=None,
            end_char=None,
        ),
        Chunk(
            id="chunk_1",
            document_id="test_doc_003",
            text="Chunk 1",
            embedding=_unit_vec(EMBEDDING_DIM, 1),
            metadata={"index": 1},
            chunk_index=1,
            start_char=None,
            end_char=None,
        ),
        Chunk(
            id="chunk_2",
            document_id="test_doc_003",
            text="Chunk 2",
            embedding=_unit_vec(EMBEDDING_DIM, 2),
            metadata={"index": 2},
            chunk_index=2,
            start_char=None,
            end_char=None,
        ),
    ]
    vector_store.upsert_chunks_batch(chunks)

    # Query closest to chunk_1
    query_embedding = _unit_vec(EMBEDDING_DIM, 1)

    results = vector_store.similarity_search(
        query_embedding=query_embedding, top_k=2, threshold=0.0
    )

    # Assertions
    assert len(results) == 2
    assert results[0].rank == 1
    assert results[1].rank == 2

    # Chunk 1 should be most similar (closest embedding)
    assert results[0].chunk.id == "chunk_1"
    assert results[0].score > 0.9  # Very high similarity


@pytest.mark.integration
def test_similarity_search_with_filters(vector_store: PgVectorStore):
    """Test similarity search with metadata filters."""
    # Setup
    doc = Document(id="test_doc_004", title="Doc", source_uri="test://", content=None)
    vector_store.upsert_document(doc)

    chunks = [
        Chunk(
            id=f"chunk_cat_{i}",
            document_id="test_doc_004",
            text=f"Chunk {i}",
            embedding=[0.1] * EMBEDDING_DIM,
            metadata={"category": "A" if i % 2 == 0 else "B"},
            chunk_index=i,
            start_char=None,
            end_char=None,
        )
        for i in range(4)
    ]
    vector_store.upsert_chunks_batch(chunks)

    # Search with filter
    results = vector_store.similarity_search(
        query_embedding=[0.1] * EMBEDDING_DIM,
        top_k=10,
        filters={"category": "A"},  # Only category A
        threshold=0.0,
    )

    # Should only return chunks with category A (2 chunks)
    assert len(results) == 2
    assert all(r.chunk.metadata["category"] == "A" for r in results)


@pytest.mark.integration
def test_batch_upsert_performance(vector_store: PgVectorStore):
    """Test batch upsert correctness (no timing assertion to avoid CI flakiness)."""
    doc = Document(id="test_doc_005", title="Doc", source_uri="test://", content=None)
    vector_store.upsert_document(doc)

    # Create 100 chunks
    chunks = [
        Chunk(
            id=f"chunk_batch_{i}",
            document_id="test_doc_005",
            text=f"Chunk {i}",
            embedding=[0.1] * EMBEDDING_DIM,  # Use config constant
            chunk_index=i,
            start_char=None,
            end_char=None,
        )
        for i in range(100)
    ]

    # Batch upsert
    vector_store.upsert_chunks_batch(chunks)

    # Verify all inserted
    results = vector_store.similarity_search(
        query_embedding=[0.1] * EMBEDDING_DIM,  # Use config constant
        top_k=100,
        threshold=0.0,
    )
    assert len(results) == 100, f"Expected 100 results, got {len(results)}"

    # Removed timing assertion (CI-flaky on shared runners)
    logger.info("✓ Batch upsert of 100 chunks verified")
