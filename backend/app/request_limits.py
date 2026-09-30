from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any


async def read_limited(
    reader: Callable[[int], Awaitable[bytes]],
    max_bytes: int,
    *,
    chunk_size: int = 1024 * 1024,
) -> bytes:
    """Read an async body source without ever accepting more than max_bytes."""
    if max_bytes <= 0 or chunk_size <= 0:
        raise ValueError("Read limits must be positive")

    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await reader(min(chunk_size, max_bytes - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValueError("Request body exceeds maximum size")
        chunks.append(chunk)
        await asyncio.sleep(0)
    return b"".join(chunks)
