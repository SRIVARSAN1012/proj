from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError


def upload_directory() -> Path:
    directory = Path(__file__).resolve().parents[2] / "uploads"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


async def save_xray(file: UploadFile, max_size_mb: int) -> str:
    if file.content_type not in {"image/png", "image/jpeg"}:
        raise ValueError("Only PNG and JPEG X-ray images are accepted")
    if not file.filename:
        raise ValueError("An image filename is required")

    content = await file.read(max_size_mb * 1024 * 1024 + 1)
    if not content:
        raise ValueError("The uploaded image is empty")
    if len(content) > max_size_mb * 1024 * 1024:
        raise ValueError(f"Image exceeds the {max_size_mb} MB upload limit")

    try:
        with Image.open(BytesIO(content)) as image:
            if image.width * image.height > 40_000_000:
                raise ValueError("Image dimensions exceed the 40-megapixel safety limit")
            image.verify()
            image_format = image.format
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValueError("The upload is not a valid image") from error
    if image_format not in {"PNG", "JPEG"}:
        raise ValueError("Only PNG and JPEG X-ray images are accepted")

    suffix = ".png" if image_format == "PNG" else ".jpg"
    image_name = f"{uuid4().hex}{suffix}"
    (upload_directory() / image_name).write_bytes(content)
    return image_name
