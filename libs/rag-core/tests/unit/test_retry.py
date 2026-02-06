"""Test retry logic."""

import pytest
from rag_core.utils.retry import retry_with_backoff


@pytest.mark.unit
def test_retry_success():
    """Test retry with eventual success."""
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.01)
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Temporary failure")
        return "success"

    result = flaky_function()
    assert result == "success"
    assert call_count == 2


@pytest.mark.unit
def test_retry_max_attempts():
    """Test retry exhaustion."""

    @retry_with_backoff(max_retries=2, initial_delay=0.01)
    def always_fails():
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        always_fails()
