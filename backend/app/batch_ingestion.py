"""Safe batch ingestion primitives for bank document folders and ZIP manifests."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
import hashlib


MAX_DOCUMENTS = 10_000
MAX_FILENAME_BYTES = 512
ALLOWED_EXTENSIONS = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"})


class IngestionKind(StrEnum):
    FOLDER_MANIFEST = "folder_manifest"
    ZIP_ARCHIVE = "zip_archive"
    STORAGE_MANIFEST = "storage_manifest"


@dataclass(frozen=True)
class IngestedFile:
    relative_path: str
    filename: str
    extension: str
    size_bytes: int
    content_sha256: str | None = None


def normalize_relative_path(path: str) -> str:
    raw = path.replace("\\", "/").strip()
    if not raw or raw.startswith("/") or ":" in raw:
        raise ValueError("Invalid relative document path")
    normalized = PurePosixPath(raw)
    if ".." in normalized.parts:
        raise ValueError("Path traversal is not allowed")
    value = str(normalized)
    if len(value.encode("utf-8")) > MAX_FILENAME_BYTES:
        raise ValueError("Document path is too long")
    return value


def validate_manifest(paths: list[str]) -> tuple[IngestedFile, ...]:
    if not paths:
        raise ValueError("No documents supplied")
    if len(paths) > MAX_DOCUMENTS:
        raise ValueError("Batch exceeds the 10,000-document safety limit")
    seen: set[str] = set()
    result: list[IngestedFile] = []
    for path in paths:
        normalized = normalize_relative_path(path)
        if normalized in seen:
            continue
        seen.add(normalized)
        suffix = PurePosixPath(normalized).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            continue
        name = PurePosixPath(normalized).name
        result.append(IngestedFile(normalized, name, suffix[1:], 0))
    if not result:
        raise ValueError("No supported document files found")
    return tuple(result)


def content_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
