"""Utility functions for rag-core.

Stage 3 hermetic rule:
- No LLM-only dependencies imported at package import time
- Text/token helpers depend on optional extras (Stage 5+)
- Only expose non-LLM utilities by default
"""

from rag_core.utils.ids import generate_id
from rag_core.utils.retry import retry_with_backoff

# Text utilities with tiktoken dependency available via explicit import:
# from rag_core.utils.text import clean_text, count_tokens, truncate_text

__all__ = [
    "generate_id",
    "retry_with_backoff",
]
