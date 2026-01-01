import os

import pytest


@pytest.mark.integration
def test_ingestion_worker_boots() -> None:
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION=1 to enable.")

    # Stage 2: ingestion-worker is a keep-alive stub.
    # Stage 4+: this will validate Redis broker + task registration.
    assert True
