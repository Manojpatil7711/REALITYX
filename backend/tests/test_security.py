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
