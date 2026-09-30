import io

import pytest
from PIL import Image
from PIL.Image import DecompressionBombError

import app.security as security


def _png(size=(8, 8)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size).save(buf, format="PNG")
    return buf.getvalue()


def test_valid_png():
    result = security.inspect_image(_png())
    assert result["integrity"]["status"] == "available"
    assert result["decoded_dimensions"]["width"] == 8
    assert result["decoded_dimensions"]["height"] == 8


def test_invalid_signature():
    with pytest.raises(ValueError, match="signature"):
        security.inspect_image(b"not-an-image")


def test_dimension_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(security, "MAX_PIXELS", 64)
    with pytest.raises(ValueError, match="dimensions"):
        security.inspect_image(_png((9, 9)))


def test_decoder_bomb_is_rejected(monkeypatch):
    def bomb_open(*args, **kwargs):
        raise DecompressionBombError("too many pixels")

    monkeypatch.setattr(security.Image, "open", bomb_open)
    with pytest.raises(ValueError, match="decoder limits"):
        security.inspect_image(_png())


def test_signature_and_decoded_format_must_agree(monkeypatch):
    class FakeImage:
        format = "JPEG"
        size = (8, 8)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def verify(self):
            return None

        def load(self):
            return None

    monkeypatch.setattr(security.Image, "open", lambda *args, **kwargs: FakeImage())
    with pytest.raises(ValueError, match="disagree"):
        security.inspect_image(_png())

from app.rate_limit import FixedWindowRateLimiter


def test_rate_limiter_blocks_after_limit_and_recovers():
    limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)
    assert limiter.check("client", now=100).allowed
    assert limiter.check("client", now=101).allowed
    blocked = limiter.check("client", now=102)
    assert not blocked.allowed
    assert blocked.retry_after_seconds == 58
    assert limiter.check("client", now=160).allowed


def test_rate_limiter_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(limit=0, window_seconds=60)
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(limit=1, window_seconds=0)


def test_rate_limiter_requires_identity():
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
    with pytest.raises(ValueError):
        limiter.check("")
