#!/usr/bin/env python3
"""Real local Valkey + RQ CPU-only smoke test; requires Valkey on localhost."""

from redis import Redis
from rq import Queue, SimpleWorker

from app.jobs import idempotent_cpu_echo

URL = "redis://127.0.0.1:6379/0"
QUEUE = "phase0c-smoke"
KEY = "phase0c-idempotency"


def consume(queue: Queue) -> None:
    SimpleWorker([queue], connection=queue.connection).work(burst=True, logging_level="WARNING")


def main() -> int:
    redis = Redis.from_url(URL)
    redis.ping()
    redis.delete(f"evs:idempotency:{KEY}")
    queue = Queue(QUEUE, connection=redis)
    queue.empty()
    first = queue.enqueue(idempotent_cpu_echo, URL, KEY, "hello")
    consume(queue)
    first.refresh()
    assert first.result == {"status": "processed", "value": "hello"}
    second = queue.enqueue(idempotent_cpu_echo, URL, KEY, "hello")
    consume(queue)  # Fresh worker instance proves basic restart behavior.
    second.refresh()
    assert second.result == {"status": "duplicate", "value": "hello"}
    print("PASS RQ enqueue/consume/restart/idempotency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
