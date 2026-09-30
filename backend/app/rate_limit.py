from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int


class FixedWindowRateLimiter:
    """Deterministic rate-limit primitive with a replaceable state backend."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("Rate-limit values must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._windows: dict[str, tuple[int, float]] = {}
        self._lock = Lock()

    def check(self, identity: str, now: float | None = None) -> RateLimitDecision:
        if not identity:
            raise ValueError("Rate-limit identity is required")
        current = monotonic() if now is None else now
        with self._lock:
            count, started = self._windows.get(identity, (0, current))
            if current - started >= self.window_seconds:
                count, started = 0, current
            if count >= self.limit:
                retry = max(1, int(self.window_seconds - (current - started) + 0.999))
                return RateLimitDecision(False, retry)
            self._windows[identity] = (count + 1, started)
            return RateLimitDecision(True, 0)


# Production multi-instance deployments must replace state with shared storage
# while preserving this interface.
image_verify_limiter = FixedWindowRateLimiter(limit=60, window_seconds=60)
