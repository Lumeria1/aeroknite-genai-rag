"""Postgres + pgvector vector store implementation."""

import logging
from typing import Any

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb, set_json_dumps, set_json_loads

from rag_core.config import EMBEDDING_DIM
from rag_core.schemas.models import Chunk, Document, RetrievalResult

logger = logging.getLogger(__name__)


class PgVectorStore:
    """
    Vector store using Postgres + pgvector.

    Features:
    - CRUD operations for documents and chunks
    - Similarity search with cosine distance
    - Metadata filtering
    - Batch operations
    """

    def __init__(self, connection_string: str):
        """
        Initialize store.

        Args:
            connection_string: Postgres connection string
                Example: "postgresql://user:pass@localhost:5432/dbname"
        """
        self.connection_string = connection_string
        self._conn: psycopg.Connection[Any] | None = None

    def connect(self) -> None:
        """Establish database connection and register type adapters."""
        if self._conn is None or self._conn.closed:
            logger.info("Connecting to Postgres...")
            self._conn = psycopg.connect(
                self.connection_string,
                row_factory=dict_row,  # Return rows as dicts
            )

            # ✅ Register pgvector adapter (list[float] <-> vector type)
            register_vector(self._conn)

            # ✅ Register JSONB adapter (dict <-> jsonb type)
            # Uses standard library json module for serialization
            import json

            set_json_dumps(json.dumps, self._conn)
            set_json_loads(json.loads, self._conn)

            logger.info("✓ Connected to Postgres (adapters registered)")

    def close(self) -> None:
        """Close database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
            logger.info("✓ Disconnected from Postgres")

    def __enter__(self) -> "PgVectorStore":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    # =========================================================================
    # Document Operations
    # =========================================================================

    def upsert_document(self, doc: Document) -> None:
        """
        Insert or update a document.

        Args:
            doc: Document to upsert
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (id, title, source_uri, content, metadata, ingested_at, updated_at)
                VALUES (%(id)s, %(title)s, %(source_uri)s, %(content)s, %(metadata)s, %(ingested_at)s, %(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    source_uri = EXCLUDED.source_uri,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    updated_at = EXCLUDED.updated_at;
                """,
                {
                    "id": doc.id,
                    "title": doc.title,
                    "source_uri": doc.source_uri,
                    "content": doc.content,
                    "metadata": Jsonb(doc.metadata or {}),
                    "ingested_at": doc.ingested_at,
                    "updated_at": doc.updated_at,
                },
            )
        self._conn.commit()
        logger.debug(f"Upserted document: {doc.id}")

    def get_document(self, doc_id: str) -> Document | None:
        """
        Retrieve document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM documents WHERE id = %s;",
                (doc_id,),
            )
            row = cur.fetchone()

        return Document(**row) if row else None

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document and all its chunks (cascade).

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
            deleted = cur.rowcount > 0

        self._conn.commit()
        logger.debug(f"Deleted document: {doc_id} (found={deleted})")
        return deleted

    # =========================================================================
    # Chunk Operations
    # =========================================================================

    def upsert_chunk(self, chunk: Chunk) -> None:
        """
        Insert or update a chunk.

        Args:
            chunk: Chunk to upsert
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunks (
                    id, document_id, text, embedding, metadata,
                    chunk_index, start_char, end_char, created_at, updated_at
                )
                VALUES (
                    %(id)s, %(document_id)s, %(text)s, %(embedding)s, %(metadata)s,
                    %(chunk_index)s, %(start_char)s, %(end_char)s, %(created_at)s, %(updated_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    text = EXCLUDED.text,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    chunk_index = EXCLUDED.chunk_index,
                    start_char = EXCLUDED.start_char,
                    end_char = EXCLUDED.end_char,
                    updated_at = EXCLUDED.updated_at;
                """,
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "embedding": chunk.embedding,
                    "metadata": Jsonb(chunk.metadata or {}),
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "created_at": chunk.created_at,
                    "updated_at": chunk.updated_at,
                },
            )
        self._conn.commit()
        logger.debug(f"Upserted chunk: {chunk.id}")

    def upsert_chunks_batch(self, chunks: list[Chunk]) -> None:
        """
        Batch upsert chunks (more efficient than individual upserts).

        Args:
            chunks: List of chunks to upsert
        """
        if not chunks:
            return

        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        with self._conn.cursor() as cur:
            # Use executemany for batch insert
            cur.executemany(
                """
                INSERT INTO chunks (
                    id, document_id, text, embedding, metadata,
                    chunk_index, start_char, end_char, created_at, updated_at
                )
                VALUES (
                    %(id)s, %(document_id)s, %(text)s, %(embedding)s, %(metadata)s,
                    %(chunk_index)s, %(start_char)s, %(end_char)s, %(created_at)s, %(updated_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    text = EXCLUDED.text,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    chunk_index = EXCLUDED.chunk_index,
                    start_char = EXCLUDED.start_char,
                    end_char = EXCLUDED.end_char,
                    updated_at = EXCLUDED.updated_at;
                """,
                [
                    {
                        "id": c.id,
                        "document_id": c.document_id,
                        "text": c.text,
                        "embedding": c.embedding,
                        "metadata": Jsonb(c.metadata or {}),
                        "chunk_index": c.chunk_index,
                        "start_char": c.start_char,
                        "end_char": c.end_char,
                        "created_at": c.created_at,
                        "updated_at": c.updated_at,
                    }
                    for c in chunks
                ],
            )
        self._conn.commit()
        logger.info(f"Batch upserted {len(chunks)} chunks")

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        """
        Retrieve chunk by ID.

        Args:
            chunk_id: Chunk ID

        Returns:
            Chunk if found, None otherwise
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM chunks WHERE id = %s;",
                (chunk_id,),
            )
            row = cur.fetchone()

        return Chunk(**row) if row else None

    # =========================================================================
    # Similarity Search
    # =========================================================================

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
        threshold: float = 0.0,
    ) -> list[RetrievalResult]:
        """
        Perform similarity search using cosine distance.

        Args:
            query_embedding: Query vector (EMBEDDING_DIM-dimensional)
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"source": "manual.pdf"})
            threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of RetrievalResult, ranked by similarity

        Example:
            results = store.similarity_search(
                query_embedding=[0.1, 0.2, ...],
                top_k=5,
                filters={"category": "technical"},
                threshold=0.7,
            )
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        if len(query_embedding) != EMBEDDING_DIM:
            raise ValueError(f"Expected {EMBEDDING_DIM}-dim embedding, got {len(query_embedding)}")

        # Build WHERE clause for metadata filters
        where_clauses = []
        params: dict[str, Any] = {
            "query_embedding": Vector(query_embedding),
            "top_k": top_k,
            "threshold": threshold,
        }

        if filters:
            # Use generated parameter names to avoid SQL injection via param names
            for i, (key, value) in enumerate(filters.items()):
                pname = f"f_{i}"
                where_clauses.append(f"metadata @> %({pname})s::jsonb")
                params[pname] = Jsonb({key: value})

        # Add similarity threshold to WHERE clause
        where_clauses.append("(1 - (embedding <=> %(query_embedding)s)) >= %(threshold)s")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Cosine similarity: 1 - cosine_distance
        # (pgvector returns distance, we convert to similarity)
        query = f"""
            SELECT
                *,
                1 - (embedding <=> %(query_embedding)s) AS similarity
            FROM chunks
            {where_sql}
            ORDER BY (embedding <=> %(query_embedding)s) ASC, id ASC

            LIMIT %(top_k)s;
        """

        with self._conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        # Convert to RetrievalResult objects
        results = []
        for rank, row in enumerate(rows, start=1):
            similarity = row.pop("similarity")
            chunk = Chunk(**row)
            results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=similarity,
                    rank=rank,
                )
            )

        logger.debug(f"Similarity search returned {len(results)} results")
        return results
