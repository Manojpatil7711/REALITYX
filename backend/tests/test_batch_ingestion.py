from app.batch_ingestion import content_sha256, normalize_relative_path, validate_manifest


def test_manifest_filters_unsupported_and_normalizes():
    files = validate_manifest(["customer/one.pdf", "customer/two.jpg", "notes.txt"])
    assert [f.relative_path for f in files] == ["customer/one.pdf", "customer/two.jpg"]


def test_manifest_rejects_traversal():
    try:
        normalize_relative_path("../secret.pdf")
    except ValueError:
        return
    assert False, "path traversal must be rejected"


def test_manifest_deduplicates_paths():
    assert len(validate_manifest(["a.pdf", "a.pdf"])) == 1


def test_content_hash():
    assert content_sha256(b"REALITYX") == content_sha256(b"REALITYX")
