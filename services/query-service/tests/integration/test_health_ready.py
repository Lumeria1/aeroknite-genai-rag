import json
import os
import time
import urllib.error
import urllib.request

import pytest


@pytest.mark.integration
def test_query_service_health_ready() -> None:
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION=1 to enable.")

    base_url = "http://localhost:8000"
    max_retries = 30
    retry_delay_seconds = 1

    def fetch(path: str) -> str:
        last_err: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(f"{base_url}{path}", timeout=5) as resp:
                    return resp.read().decode("utf-8")
            except (urllib.error.URLError, OSError) as e:
                last_err = e
                if attempt < max_retries:
                    time.sleep(retry_delay_seconds)
        total_wait_seconds = retry_delay_seconds * (max_retries - 1)
        raise AssertionError(
            f"Failed to reach {path} after {max_retries} attempts "
            f"({total_wait_seconds}s total wait): {last_err}"
        )

    health = json.loads(fetch("/health"))
    ready = json.loads(fetch("/ready"))

    assert health.get("status") == "ok"
    assert ready.get("status") == "ready"
