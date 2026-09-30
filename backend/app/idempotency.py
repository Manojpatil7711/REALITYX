from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Any


@dataclass(frozen=True)
class CachedResponse:
    fingerprint: str
    response: Any
    expires_at: float


class IdempotencyStore:
    def __init__(self, ttl_seconds: int = 3600, max_items: int = 10000) -> None:
        if ttl_seconds <= 0 or max_items <= 0:
            raise ValueError("Idempotency limits must be positive")
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._items: dict[str, CachedResponse] = {}
        self._lock = Lock()

    def get(self, key: str, fingerprint: str) -> Any | None:
        now = monotonic()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            if item.expires_at <= now:
                del self._items[key]
                return None
            if item.fingerprint != fingerprint:
                raise ValueError("Idempotency-Key was reused for a different request")
            return item.response

    def put(self, key: str, fingerprint: str, response: Any) -> None:
        now = monotonic()
        with self._lock:
            expired = [k for k, item in self._items.items() if item.expires_at <= now]
            for expired_key in expired:
                del self._items[expired_key]

            if key not in self._items and len(self._items) >= self.max_items:
                oldest_key = min(self._items, key=lambda k: self._items[k].expires_at)
                del self._items[oldest_key]

            self._items[key] = CachedResponse(
                fingerprint=fingerprint,
                response=response,
                expires_at=now + self.ttl_seconds,
            )


store = IdempotencyStore()
