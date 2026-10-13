"""Security helpers and validation placeholders for the research backend."""

from __future__ import annotations


def validate_upload_metadata(filename: str, content_type: str | None) -> None:
    if not filename:
        raise ValueError("Upload filename is required")
    if content_type and content_type not in {"image/png", "image/jpeg"}:
        raise ValueError("Unsupported content type")
