import pytest
from PIL import Image
import io
from app.security import inspect_image

def test_valid_png():
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, format="PNG")
    result = inspect_image(buf.getvalue())
    assert result["integrity"]["status"] == "available"

def test_invalid_signature():
    with pytest.raises(ValueError):
        inspect_image(b"not-an-image")
