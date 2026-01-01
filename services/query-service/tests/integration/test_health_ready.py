import os
import time
import pytest
import urllib.request
import urllib.error


@pytest.mark.integration
def test_query_service_health_ready() -> None:
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION=1 to enable.")

    base_url = "http://localhost:8000"
    max_retries = 30
    delay_s = 1

    def fetch(path: str) -> str:
        last_err: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(f"{base_url}{path}", timeout=5) as resp:
                    return resp.read().decode("utf-8")
            except (urllib.error.URLError, OSError) as e:
                last_err = e
                time.sleep(delay_s)
        total_wait_s = delay_s * max_retries
        raise AssertionError(
            f"Failed to reach {path} after {max_retries} attempts "
            f"({total_wait_s}s total wait): {last_err}"
        )

    health = fetch("/health")
    ready = fetch("/ready")

    assert "ok" in health
    assert "ready" in ready
