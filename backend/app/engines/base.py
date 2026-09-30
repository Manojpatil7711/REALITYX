from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EngineContext:
    verification_id: str
    media_sha256: str

class SignalEngine(ABC):
    name: str
    version: str = "0.1.0"

    @abstractmethod
    def analyze(self, data: bytes, context: EngineContext) -> dict[str, Any]:
        raise NotImplementedError
