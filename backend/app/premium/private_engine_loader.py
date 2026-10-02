"""Load optional proprietary engines without publishing their implementation.

The public core defines the contract; proprietary research engines can live in a
private server package and be enabled explicitly by deployment configuration.
The private package is never trusted as a source of policy: engines still return
ordinary Evidence-compatible results and failures are isolated by the pipeline.
"""

from __future__ import annotations

import importlib
import os
from collections.abc import Iterable
from typing import Any

from ..engines.base import SignalEngine

_ENV_NAME = "REALITYX_PRIVATE_ENGINE_MODULE"
_ALLOWED_PREFIX = "realityx_private."


def load_private_engines() -> tuple[type[SignalEngine], ...]:
    """Return deployment-owned engines, or an empty tuple when none are configured."""
    module_name = os.getenv(_ENV_NAME, "").strip()
    if not module_name:
        return ()
    if not module_name.startswith(_ALLOWED_PREFIX):
        raise RuntimeError(f"{_ENV_NAME} must use the {_ALLOWED_PREFIX!r} namespace")

    module = importlib.import_module(module_name)
    factory = getattr(module, "get_engines", None)
    if not callable(factory):
        raise RuntimeError(f"{module_name} must expose get_engines()")

    engines: Any = factory()
    if not isinstance(engines, Iterable):
        raise RuntimeError("get_engines() must return an iterable of engine classes")

    result: list[type[SignalEngine]] = []
    for engine_type in engines:
        if not isinstance(engine_type, type) or not issubclass(engine_type, SignalEngine):
            raise RuntimeError("private engine registry contains an invalid engine")
        result.append(engine_type)
    return tuple(result)
