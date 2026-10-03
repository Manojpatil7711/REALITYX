from __future__ import annotations

from threading import Lock

from .contracts import VerificationArtifact


class ReceiptStore:
    """Bounded in-memory receipt registry; replace with durable storage in production."""

    def __init__(self, max_items: int = 10000) -> None:
        if max_items <= 0:
            raise ValueError("Receipt store limit must be positive")
        self.max_items = max_items
        self._items: dict[str, VerificationArtifact] = {}
        self._lock = Lock()

    def put(self, artifact: VerificationArtifact) -> None:
        with self._lock:
            if artifact.verification_id not in self._items and len(self._items) >= self.max_items:
                oldest_key = next(iter(self._items))
                del self._items[oldest_key]
            self._items[artifact.verification_id] = artifact

    def get(self, verification_id: str) -> VerificationArtifact | None:
        with self._lock:
            return self._items.get(verification_id)


store = ReceiptStore()
