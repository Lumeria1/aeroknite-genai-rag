"""Configuration constants for rag-core."""

import os

# Embedding dimension (OpenAI text-embedding-3-small standard)
# Can be overridden via RAG_EMBEDDING_DIM environment variable
EMBEDDING_DIM = int(os.getenv("RAG_EMBEDDING_DIM", "1536"))

# Supported embedding dimensions (for validation)
SUPPORTED_EMBEDDING_DIMS = {
    1536,  # text-embedding-3-small, text-embedding-ada-002
    3072,  # text-embedding-3-large
}


def validate_embedding_dim(dim: int) -> None:
    """
    Validate embedding dimension.

    Args:
        dim: Dimension to validate

    Raises:
        ValueError: If dimension not supported
    """
    if dim not in SUPPORTED_EMBEDDING_DIMS:
        raise ValueError(
            f"Unsupported embedding dimension: {dim}. " f"Supported: {SUPPORTED_EMBEDDING_DIMS}"
        )


# Embedding dimension (OpenAI standard)
# Can be overridden via RAG_EMBEDDING_DIM environment variable
EMBEDDING_DIM = int(os.getenv("RAG_EMBEDDING_DIM", "1536"))

# 🔒 Validate at import time so downstream modules can assume correctness
validate_embedding_dim(EMBEDDING_DIM)
