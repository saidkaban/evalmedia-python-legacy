"""Tests for image utilities."""

import asyncio
import base64
import io
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from evalmedia.image_utils import image_to_base64, image_to_bytes, load_image


class TestLoadImage:
    def test_load_pil_image(self):
        img = Image.new("RGB", (100, 100), "red")
        result = asyncio.run(load_image(img))
        assert result is img
        assert result.size == (100, 100)

    def test_load_bytes(self):
        img = Image.new("RGB", (100, 100), "blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        raw = buffer.getvalue()

        result = asyncio.run(load_image(raw))
        assert result.size == (100, 100)

    def test_load_file_path_str(self):
        img = Image.new("RGB", (100, 100), "green")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            path = f.name

        result = asyncio.run(load_image(path))
        assert result.size == (100, 100)
        Path(path).unlink()

    def test_load_file_path_object(self):
        img = Image.new("RGB", (100, 100), "yellow")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            path = Path(f.name)

        result = asyncio.run(load_image(path))
        assert result.size == (100, 100)
        path.unlink()

    def test_load_base64_data_uri(self):
        img = Image.new("RGB", (50, 50), "white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()
        data_uri = f"data:image/png;base64,{b64}"

        result = asyncio.run(load_image(data_uri))
        assert result.size == (50, 50)

    def test_load_unsupported_type(self):
        with pytest.raises(TypeError, match="Unsupported"):
            asyncio.run(load_image(12345))


class TestImageConversion:
    def test_image_to_base64(self):
        img = Image.new("RGB", (50, 50), "purple")
        b64 = image_to_base64(img)
        assert isinstance(b64, str)
        assert len(b64) > 0
        # Verify it decodes back
        decoded = base64.b64decode(b64)
        recovered = Image.open(io.BytesIO(decoded))
        assert recovered.size == (50, 50)

    def test_image_to_bytes(self):
        img = Image.new("RGB", (50, 50), "orange")
        raw = image_to_bytes(img)
        assert isinstance(raw, bytes)
        recovered = Image.open(io.BytesIO(raw))
        assert recovered.size == (50, 50)
