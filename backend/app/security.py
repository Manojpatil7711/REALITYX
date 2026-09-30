import io
from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_WIDTH = 12000
MAX_HEIGHT = 12000
MAX_PIXELS = 80_000_000

MAGIC = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp": b"RIFF",
}

def _magic_type(data: bytes) -> str | None:
    if data.startswith(MAGIC["jpeg"]):
        return "jpeg"
    if data.startswith(MAGIC["png"]):
        return "png"
    if data.startswith(MAGIC["webp"]) and data[8:12] == b"WEBP":
        return "webp"
    return None

def inspect_image(data: bytes) -> dict:
    kind = _magic_type(data)
    if kind is None:
        raise ValueError("Unsupported or invalid image signature")

    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            if width > MAX_WIDTH or height > MAX_HEIGHT or width * height > MAX_PIXELS:
                raise ValueError("Decoded image dimensions exceed safety limits")
            return {
                "integrity": {"status": "available", "format": kind},
                "decoded_dimensions": {"status": "available", "width": width, "height": height},
                "metadata": {"status": "available"},
            }
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Corrupt or malformed image") from exc
