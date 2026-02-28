from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps


@dataclass(frozen=True)
class ImageDecodeResult:
    rgb: np.ndarray  # HWC uint8 RGB
    width: int
    height: int


def decode_image_bytes(image_bytes: bytes) -> ImageDecodeResult:
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img).convert("RGB")
    arr = np.asarray(img, dtype=np.uint8)
    h, w = arr.shape[:2]
    return ImageDecodeResult(rgb=arr, width=w, height=h)


def resize_rgb(rgb: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize(size, resample=Image.BILINEAR)
    return np.asarray(img, dtype=np.uint8)

