"""Image loading and conversion utilities."""

from __future__ import annotations

import base64
import io
from pathlib import Path

import httpx
from PIL import Image

ImageInput = str | Path | Image.Image | bytes


async def load_image(source: ImageInput) -> Image.Image:
    """Normalize any image input to a PIL Image.

    Accepts:
        - PIL.Image.Image (returned as-is)
        - bytes (decoded)
        - str file path or URL
        - pathlib.Path
    """
    if isinstance(source, Image.Image):
        return source

    if isinstance(source, bytes):
        return Image.open(io.BytesIO(source))

    if isinstance(source, Path):
        return Image.open(source)

    if isinstance(source, str):
        # Check if it's a base64 string
        if source.startswith("data:image"):
            # data URI: data:image/png;base64,<data>
            _, encoded = source.split(",", 1)
            return Image.open(io.BytesIO(base64.b64decode(encoded)))

        # Check if it looks like base64 (no path separators, long enough)
        if len(source) > 200 and "/" not in source and "\\" not in source:
            try:
                return Image.open(io.BytesIO(base64.b64decode(source)))
            except Exception:
                pass

        # Check if it's a URL
        if source.startswith(("http://", "https://")):
            async with httpx.AsyncClient() as client:
                response = await client.get(source, follow_redirects=True)
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content))

        # Treat as file path
        return Image.open(source)

    raise TypeError(f"Unsupported image input type: {type(source)}")


def load_image_sync(source: ImageInput) -> Image.Image:
    """Synchronous version of load_image."""
    import asyncio

    return asyncio.run(load_image(source))


def image_to_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """Convert a PIL Image to a base64-encoded string."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    """Convert a PIL Image to raw bytes."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()
