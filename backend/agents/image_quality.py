from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class ImageQualityResult:
    ok: bool
    blur_score: float
    brightness_mean: float
    contrast_std: float
    noise_score: float
    reasons: list[str]


def assess_image_quality(rgb_uint8: np.ndarray) -> ImageQualityResult:
    """
    Lightweight heuristics (not a medical-grade validator):
    - blur_score: variance of Laplacian on grayscale
    - brightness_mean: mean grayscale intensity
    - contrast_std: stddev grayscale intensity
    - noise_score: mean absolute difference between image and median blur
    """
    gray = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_mean = float(np.mean(gray))
    contrast_std = float(np.std(gray))

    med = cv2.medianBlur(gray, 5)
    noise_score = float(np.mean(np.abs(gray.astype(np.float32) - med.astype(np.float32))))

    reasons: list[str] = []
    ok = True

    if blur_score < 60.0:
        ok = False
        reasons.append("Image looks blurry (low edge detail).")
    if brightness_mean < 40.0:
        ok = False
        reasons.append("Image is too dark.")
    if brightness_mean > 215.0:
        ok = False
        reasons.append("Image is too bright / washed out.")
    if contrast_std < 25.0:
        ok = False
        reasons.append("Low contrast (hard to see agglutination patterns).")

    # Blood Sample Detection (Redness/Color-based)
    avg_color = np.mean(rgb_uint8, axis=(0, 1))
    r_to_g = avg_color[0] / (avg_color[1] + 1e-6)
    r_to_b = avg_color[0] / (avg_color[2] + 1e-6)
    
    # Simple check for red/pink dominance
    if r_to_g < 1.05 or r_to_b < 1.1:
        ok = False
        reasons.append("Invalid sample: Image does not appear to be a blood sample.")

    return ImageQualityResult(
        ok=ok,
        blur_score=blur_score,
        brightness_mean=brightness_mean,
        contrast_std=contrast_std,
        noise_score=noise_score,
        reasons=reasons,
    )


def to_dict(r: ImageQualityResult) -> dict[str, Any]:
    return {
        "ok": r.ok,
        "blurScore": r.blur_score,
        "brightnessMean": r.brightness_mean,
        "contrastStd": r.contrast_std,
        "noiseScore": r.noise_score,
        "reasons": r.reasons,
    }

