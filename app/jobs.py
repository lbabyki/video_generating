from redis import Redis


def cpu_echo(value: str) -> dict[str, str]:
    return {"status": "processed", "value": value}


def idempotent_cpu_echo(valkey_url: str, idempotency_key: str, value: str) -> dict[str, str]:
    redis = Redis.from_url(valkey_url)
    if not redis.set(f"evs:idempotency:{idempotency_key}", "1", nx=True, ex=3600):
        return {"status": "duplicate", "value": value}
    return cpu_echo(value)
