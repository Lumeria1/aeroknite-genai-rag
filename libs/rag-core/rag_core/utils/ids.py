"""ID generation utilities."""

from uuid import uuid4


def generate_id(prefix: str = "") -> str:
    """
    Generate unique ID.

    Args:
        prefix: Optional prefix (e.g., "chunk", "doc")

    Returns:
        Unique ID string

    Example:
        >>> generate_id("chunk")
        "chunk_a1b2c3d4e5f6"
    """
    suffix = uuid4().hex[:12]
    return f"{prefix}_{suffix}" if prefix else suffix
