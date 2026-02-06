"""Pytest fixtures for rag-core tests."""

import os
from collections.abc import Generator

import psycopg
import pytest
from psycopg import Connection
from rag_core.stores.migrations import drop_schema, ensure_schema
from rag_core.stores.pgvector_store import PgVectorStore


@pytest.fixture(scope="session")
def postgres_connection_string() -> str:
    """Postgres connection string for tests."""
    return os.getenv(
        "TEST_POSTGRES_URL",
        "postgresql://postgres:postgres@localhost:5432/rag",
    )


@pytest.fixture(scope="function")
def pg_conn(postgres_connection_string: str) -> Generator[Connection, None, None]:
    """
    Postgres connection with schema setup/teardown.

    Function-scoped: Each test gets a clean schema.
    """
    # Skip if integration tests disabled
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Integration tests disabled (set RUN_INTEGRATION=1)")

    conn = psycopg.connect(postgres_connection_string)

    try:
        # Setup: Create schema
        ensure_schema(conn)

        yield conn

    finally:
        # Teardown: Drop schema (rollback first if in failed transaction)
        try:
            # If transaction is in error state, rollback before dropping
            if conn.info.transaction_status == psycopg.pq.TransactionStatus.INERROR:
                conn.rollback()

            drop_schema(conn)
        except Exception as e:
            # Log but don't fail teardown
            print(f"Warning: Schema cleanup failed: {e}")
        finally:
            conn.close()


@pytest.fixture(scope="function")
def vector_store(
    pg_conn: Connection, postgres_connection_string: str
) -> Generator[PgVectorStore, None, None]:
    """Vector store instance for tests."""
    store = PgVectorStore(postgres_connection_string)
    store.connect()

    # Ensure store is cleaned up after test
    yield store

    if store._conn and not store._conn.closed:
        store.close()
