from redis import Redis
from rq import Queue

from app.core.config import settings


def default_queue() -> Queue:
    """Construct only; callers decide when to connect/enqueue."""
    return Queue("video", connection=Redis.from_url(settings.valkey_url))
