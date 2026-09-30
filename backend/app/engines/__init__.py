from .base import EngineContext, SignalEngine
from .integrity import IntegrityEngine

ENGINE_REGISTRY: tuple[type[SignalEngine], ...] = (IntegrityEngine,)
