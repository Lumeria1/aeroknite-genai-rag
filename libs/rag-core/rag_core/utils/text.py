"""Text processing utilities.

NOTE: Token counting functions require tiktoken (optional dependency).
Install with: pip install -e 'libs/rag-core[llm]'
"""

import re
from typing import cast


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    # Remove multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove multiple spaces
    text = re.sub(r" {2,}", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def _get_tiktoken():
    """Lazy import tiktoken (raises helpful error if not installed)."""
    try:
        import tiktoken

        return tiktoken
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "tiktoken is required for token counting but is not installed.\n"
            "Install rag-core with LLM extras:\n"
            "  pip install -e 'libs/rag-core[llm]'\n"
            "Or install tiktoken directly:\n"
            "  pip install tiktoken"
        ) from e


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens using tiktoken (accurate for OpenAI models).

    Requires: tiktoken (install via [llm] extras)

    Args:
        text: Text to count
        model: Model name (for correct encoding)

    Returns:
        Token count
    """
    tiktoken = _get_tiktoken()
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def truncate_text(text: str, max_tokens: int, model: str = "gpt-4o-mini") -> str:
    """
    Truncate text to fit within token limit.

    Requires: tiktoken (install via [llm] extras)

    Args:
        text: Text to truncate
        max_tokens: Maximum tokens
        model: Model name

    Returns:
        Truncated text
    """
    tiktoken = _get_tiktoken()
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return text

    truncated_tokens = tokens[:max_tokens]
    return cast(str, encoding.decode(truncated_tokens))
