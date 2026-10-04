from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic
import hashlib


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int


class FixedWindowRateLimiter:
    """Deterministic rate-limit primitive with a replaceable state backend."""

    def __init__(self, limit: int, window_seconds: int, max_identities: int = 10000) -> None:
        if limit <= 0 or window_seconds <= 0 or max_identities <= 0:
            raise ValueError("Rate-limit values must be positive")
        self.max_identities = max_identities
        self.limit = limit
        self.window_seconds = window_seconds
        self._windows: dict[str, tuple[int, float]] = {}
        self._lock = Lock()

    def check(self, identity: str, now: float | None = None) -> RateLimitDecision:
        if not identity:
            raise ValueError("Rate-limit identity is required")
        current = monotonic() if now is None else now
        with self._lock:
            expired = [key for key, (_, started) in self._windows.items() if current - started >= self.window_seconds]
            for key in expired:
                del self._windows[key]
            if len(self._windows) >= self.max_identities and identity not in self._windows:
                oldest = min(self._windows, key=lambda key: self._windows[key][1])
                del self._windows[oldest]
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
receipt_read_limiter = FixedWindowRateLimiter(limit=120, window_seconds=60)
receipt_verify_limiter = FixedWindowRateLimiter(limit=60, window_seconds=60)



def privacy_rate_limit_identity(scope: str, principal: str, client: str | None = None) -> str:
    """Build a bounded, non-raw rate-limit identity for layered abuse controls."""
    if not scope or not principal:
        raise ValueError("Rate-limit scope and principal are required")
    material = f"{scope}|{principal}|{client or 'unknown'}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


agent_key_limiter = FixedWindowRateLimiter(limit=120, window_seconds=60)
