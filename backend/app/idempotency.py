from dataclasses import dataclass
from threading import Lock
from typing import Any

@dataclass(frozen=True)
class CachedResponse:
    fingerprint: str
    response: Any

class IdempotencyStore:
    def __init__(self) -> None:
        self._items: dict[str, CachedResponse] = {}
        self._lock = Lock()

    def get(self, key: str, fingerprint: str) -> Any | None:
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            if item.fingerprint != fingerprint:
                raise ValueError("Idempotency-Key was reused for a different request")
            return item.response

    def put(self, key: str, fingerprint: str, response: Any) -> None:
        with self._lock:
            self._items[key] = CachedResponse(fingerprint, response)

store = IdempotencyStore()
