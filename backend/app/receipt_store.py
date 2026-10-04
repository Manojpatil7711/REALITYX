from __future__ import annotations

from threading import Lock

from .contracts import VerificationArtifact


class ReceiptStore:
    """Bounded process-local receipt registry.

    This is intentionally an in-memory cache, not durable production storage.
    A durable implementation must preserve receipt lookup across restarts and
    across multiple application instances.
    """

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
            self._items[artifact.verification_id] = artifact.model_copy(deep=True)

    def get(self, verification_id: str) -> VerificationArtifact | None:
        with self._lock:
            artifact = self._items.get(verification_id)
            return artifact.model_copy(deep=True) if artifact is not None else None


store = ReceiptStore()
