"""Safe batch ingestion primitives for bank document folders and ZIP manifests."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
import hashlib
from io import BytesIO
from zipfile import BadZipFile, ZipFile


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


MAX_ZIP_BYTES = 100 * 1024 * 1024
MAX_ZIP_UNCOMPRESSED_BYTES = 500 * 1024 * 1024
MAX_ZIP_ENTRY_BYTES = 25 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO = 100


@dataclass(frozen=True)
class ZipEntry:
    relative_path: str
    size_bytes: int
    compressed_size_bytes: int
    extension: str


def validate_zip_archive(data: bytes) -> tuple[ZipEntry, ...]:
    """Validate ZIP metadata without extracting untrusted files."""
    if not data:
        raise ValueError("ZIP archive must not be empty")
    if len(data) > MAX_ZIP_BYTES:
        raise ValueError("ZIP archive exceeds maximum size")
    try:
        archive = ZipFile(BytesIO(data))
    except (BadZipFile, OSError) as exc:
        raise ValueError("Invalid ZIP archive") from exc
    entries: list[ZipEntry] = []
    total_uncompressed = 0
    seen: set[str] = set()
    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_DOCUMENTS:
            raise ValueError("ZIP contains too many entries")
        for info in infos:
            raw = info.filename
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ValueError("ZIP symlinks are not allowed")
            normalized = normalize_relative_path(raw)
            if normalized in seen:
                raise ValueError("ZIP contains duplicate document paths")
            seen.add(normalized)
            if info.is_dir():
                continue
            if info.file_size > MAX_ZIP_ENTRY_BYTES:
                raise ValueError("ZIP entry exceeds maximum file size")
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_ZIP_UNCOMPRESSED_BYTES:
                raise ValueError("ZIP uncompressed size exceeds safety limit")
            if info.file_size and info.compress_size and info.file_size / info.compress_size > MAX_ZIP_COMPRESSION_RATIO:
                raise ValueError("ZIP compression ratio exceeds safety limit")
            suffix = PurePosixPath(normalized).suffix.lower()
            if suffix not in ALLOWED_EXTENSIONS:
                continue
            entries.append(ZipEntry(normalized, info.file_size, info.compress_size, suffix[1:]))
    if not entries:
        raise ValueError("No supported document files found in ZIP")
    return tuple(entries)

def content_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
