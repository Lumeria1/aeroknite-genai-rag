# rag-core

Shared RAG primitives for Aeroknite GenAI system.

## Purpose

This library provides core RAG functionality used by both `query-service` and `ingestion-worker`:

-   **Vector Store**: Postgres + pgvector CRUD operations
-   **Retrieval**: Similarity search with metadata filtering
-   **Grading**: LLM-based relevance and groundedness checking
-   **Schemas**: Shared data models (Chunk, Document, Citation)

## Installation

From repository root:

```bash
pip install -e libs/rag-core
```

## Usage

```python
from rag_core.stores import PgVectorStore
from rag_core.schemas import Chunk

# Initialize store
store = PgVectorStore(connection_string="postgresql://...")

# Store chunks
chunk = Chunk(
    id="chunk_001",
    text="Example text",
    embedding=[0.1, 0.2, ...],
    metadata={"source": "doc1.pdf"}
)
store.upsert(chunk)

# Search
results = store.similarity_search(
    query_embedding=[0.1, 0.2, ...],
    top_k=5,
    filters={"source": "doc1.pdf"}
)
```

## Testing

```bash
# Unit tests (fast)
pytest tests/unit -m unit

# Integration tests (requires Postgres)
RUN_INTEGRATION=1 pytest tests/integration -m integration
```

## Architecture

-   **stores/**: Vector database operations
-   **retrieval/**: Query logic, reranking, filtering
-   **grading/**: LLM-based evaluation
-   **schemas/**: Pydantic models
-   **utils/**: Helpers (text processing, retries, etc.)
