import pytest

from app.request_limits import read_limited


def test_read_limited_accepts_exact_boundary():
    chunks = [b"abc", b"def"]

    async def reader(size: int) -> bytes:
        return chunks.pop(0) if chunks else b""

    assert __import__("asyncio").run(read_limited(reader, 6, chunk_size=3)) == b"abcdef"


def test_read_limited_rejects_overflow():
    chunks = [b"abc", b"def"]

    async def reader(size: int) -> bytes:
        return chunks.pop(0) if chunks else b""

    with pytest.raises(ValueError, match="maximum size"):
        __import__("asyncio").run(read_limited(reader, 5, chunk_size=3))


def test_read_limited_rejects_invalid_limits():
    async def reader(size: int) -> bytes:
        return b""

    with pytest.raises(ValueError):
        __import__("asyncio").run(read_limited(reader, 0))
