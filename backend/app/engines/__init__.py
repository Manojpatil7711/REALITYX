from .base import EngineContext, SignalEngine
from .integrity import IntegrityEngine
from .structure import StructureEngine
from ..premium.private_engine_loader import load_private_engines

_BUILTIN_ENGINES: tuple[type[SignalEngine], ...] = (
    IntegrityEngine,
    StructureEngine,
)

# Proprietary engines are deployment-owned and never shipped in the public repository.
ENGINE_REGISTRY: tuple[type[SignalEngine], ...] = _BUILTIN_ENGINES + load_private_engines()
