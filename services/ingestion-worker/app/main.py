import time


def main() -> None:
    # Stage 4+: this will become Celery worker process.
    # Stage 2: keep alive so docker-compose boot + healthchecks work.
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
