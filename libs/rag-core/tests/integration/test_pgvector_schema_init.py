"""Test schema initialization."""

import pytest
from psycopg import Connection
from psycopg.errors import ForeignKeyViolation
from rag_core.config import EMBEDDING_DIM


@pytest.mark.integration
def test_schema_initialization(pg_conn: Connection):
    """Test schema is created correctly."""
    with pg_conn.cursor() as cur:
        # Check pgvector extension
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        assert cur.fetchone() is not None, "pgvector extension not found"

        # Check documents table
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'documents';
            """
        )
        assert cur.fetchone() is not None, "documents table not found"

        # Check chunks table
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'chunks';
            """
        )
        assert cur.fetchone() is not None, "chunks table not found"

        # Check vector index (accept either HNSW or IVFFlat)
        cur.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'chunks'
              AND indexname IN ('chunks_embedding_hnsw_idx', 'chunks_embedding_ivfflat_idx');
            """
        )
        assert cur.fetchone() is not None, "Vector index not found (HNSW or IVFFlat)"


@pytest.mark.integration
def test_foreign_key_constraint(pg_conn: Connection):
    """Test document-chunk foreign key works."""
    with pg_conn.cursor() as cur:
        dummy_embedding = [0.1] * EMBEDDING_DIM

        with pytest.raises(ForeignKeyViolation):
            cur.execute(
                """
                INSERT INTO chunks (id, document_id, text, embedding)
                VALUES (%s, %s, %s, %s);
                """,
                ("test_chunk", "nonexistent_doc", "test text", dummy_embedding),
            )

    # Rollback the failed transaction so fixture teardown works
    pg_conn.rollback()
