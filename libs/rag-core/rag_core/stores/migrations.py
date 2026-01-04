"""Database schema initialization and migrations."""

import logging
from typing import Any

import psycopg
from psycopg import sql

from rag_core.config import EMBEDDING_DIM

logger = logging.getLogger(__name__)


def ensure_schema(conn: psycopg.Connection[Any]) -> None:
    """
    Ensure pgvector extension and required tables exist.

    REQUIREMENTS:
    - Postgres >= 16
    - pgvector >= 0.7.0 (for HNSW index support)

    This is idempotent and safe to call on every startup.

    Args:
        conn: Active Postgres connection

    Raises:
        psycopg.Error: If schema creation fails
    """
    logger.info(f"Ensuring pgvector schema (embedding_dim={EMBEDDING_DIM})...")

    with conn.cursor() as cur:
        # 1. Enable pgvector extension
        logger.info("Enabling pgvector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Check pgvector version
        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
        version = cur.fetchone()
        if version:
            logger.info(f"pgvector version: {version[0]}")

        # 2. Create documents table
        logger.info("Creating documents table...")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source_uri TEXT NOT NULL,
                content TEXT,
                metadata JSONB DEFAULT '{}',
                ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """
        )

        # 3. Create chunks table with dynamic embedding dimension
        logger.info(f"Creating chunks table (vector({EMBEDDING_DIM}))...")

        # Construct SQL with embedding dimension (safe: EMBEDDING_DIM is validated int)
        dim_sql = sql.SQL(str(EMBEDDING_DIM))

        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    embedding vector({dim}) NOT NULL,
                    metadata JSONB DEFAULT '{{}}',
                    chunk_index INTEGER NOT NULL DEFAULT 0,
                    start_char INTEGER,
                    end_char INTEGER,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """
            ).format(dim=dim_sql)
        )

        # 4. Create indexes for performance
        logger.info("Creating indexes...")

        # Vector similarity index
        # Try HNSW first (requires pgvector >= 0.7, Postgres >= 16)
        # Fall back to IVFFlat if HNSW unavailable
        try:
            logger.info("Creating HNSW index (optimal for <1M vectors)...")
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
                ON chunks USING hnsw (embedding vector_cosine_ops);
            """
            )
            logger.info("✓ HNSW index created")
        except psycopg.Error as e:
            logger.warning(f"HNSW index creation failed, falling back to IVFFlat: {e}")
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS chunks_embedding_ivfflat_idx
                ON chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """
            )
            logger.info("✓ IVFFlat index created (fallback)")

        # Document foreign key index
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS chunks_document_id_idx
            ON chunks(document_id);
        """
        )

        # Metadata JSONB index (GIN for fast JSON queries)
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS chunks_metadata_idx
            ON chunks USING gin (metadata);
        """
        )

        # Timestamp indexes for time-based queries
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS chunks_created_at_idx
            ON chunks(created_at);
        """
        )

    conn.commit()
    logger.info("✓ Schema initialization complete")


def drop_schema(conn: psycopg.Connection[Any]) -> None:
    """
    Drop all tables (for testing cleanup).

    ⚠️ DESTRUCTIVE - Only use in tests.

    Args:
        conn: Active Postgres connection
    """
    logger.warning("Dropping schema (testing only)...")

    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS chunks CASCADE;")
        cur.execute("DROP TABLE IF EXISTS documents CASCADE;")

    conn.commit()
    logger.info("✓ Schema dropped")
