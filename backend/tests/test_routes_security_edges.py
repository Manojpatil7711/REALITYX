import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_empty_image_upload_is_rejected():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty"


def test_unsupported_image_signature_is_rejected():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("payload.bin", b"not-an-image", "application/octet-stream")},
    )
    assert response.status_code == 415
    assert "invalid image format" in response.json()["detail"]


def test_idempotency_key_cannot_be_reused_for_different_content():
    import io
    from PIL import Image

    def png(size):
        buffer = io.BytesIO()
        Image.new("RGB", size).save(buffer, format="PNG")
        return buffer.getvalue()

    key = str(uuid.uuid4())
    first = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("first.png", png((16, 10)), "image/png")},
    )
    second = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("second.png", png((8, 8)), "image/png")},
    )
    assert first.status_code == 200
    assert second.status_code == 409
