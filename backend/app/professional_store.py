from __future__ import annotations

from threading import Lock

from .contracts import VerificationResponse


class ProfessionalResponseStore:
    """Bounded process-local cache for professional report generation.

    Production deployments should replace this with durable, access-controlled
    storage before relying on historical reports across restarts/instances.
    """

    def __init__(self, max_items: int = 10000) -> None:
        self.max_items = max_items
        self._items: dict[str, VerificationResponse] = {}
        self._lock = Lock()

    def put(self, response: VerificationResponse) -> None:
        with self._lock:
            if response.verification_id not in self._items and len(self._items) >= self.max_items:
                oldest = next(iter(self._items))
                del self._items[oldest]
            self._items[response.verification_id] = response.model_copy(deep=True)

    def get(self, verification_id: str) -> VerificationResponse | None:
        with self._lock:
            response = self._items.get(verification_id)
            return response.model_copy(deep=True) if response is not None else None


store = ProfessionalResponseStore()
