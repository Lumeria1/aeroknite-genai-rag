"""
rag-core: Shared RAG primitives for Aeroknite GenAI system.

This package provides:
- Vector store operations (Postgres + pgvector)
- Retrieval and reranking logic
- Deterministic grading functions (LLM-based graders in Stage 5+)
- Shared data schemas
"""

__version__ = "0.1.0"

# Export config
from rag_core.config import EMBEDDING_DIM, validate_embedding_dim

# Export commonly used classes
from rag_core.schemas.models import Chunk, Citation, Document, RetrievalResult
from rag_core.stores.pgvector_store import PgVectorStore

__all__ = [
    "EMBEDDING_DIM",
    "validate_embedding_dim",
    "Chunk",
    "Document",
    "RetrievalResult",
    "Citation",
    "PgVectorStore",
]
