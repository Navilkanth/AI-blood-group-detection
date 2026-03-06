import cv2
import numpy as np
from typing import Any, Literal

Sex = Literal["male", "female", "other"]


def estimate_hb_from_image(rgb_uint8: np.ndarray) -> float:
    """
    Crude heuristic for demo: uses the redness (R-G-B) of the image.
    In real clinical settings, this would require spectral analysis or calibration.
    """
    # Average color across the whole image
    avg_color = np.mean(rgb_uint8, axis=(0, 1))
    r, g, b = avg_color[0], avg_color[1], avg_color[2]
    
    # Blood redness intensity (higher red relative to G/B)
    redness = max(0, r - (g + b) / 2)
    
    # Map redness to a plausible Hb range (e.g., 0-18 g/dL)
    hb_estimate = 6.0 + (redness / 100.0) * 12.0
    return min(18.0, max(5.0, hb_estimate))


def check_hemoglobin(hb_g_dl: float, sex: Sex) -> dict[str, Any]:
    """
    Rule-based categorization using common adult reference ranges.
    Not a diagnostic tool.
    """
    if hb_g_dl <= 0:
        raise ValueError("Hemoglobin must be > 0")

    # Broad adult ranges (lab ranges vary).
    if sex == "male":
        low, high = 13.5, 17.5
    elif sex == "female":
        low, high = 12.0, 15.5
    else:
        low, high = 12.5, 16.5

    if hb_g_dl < low:
        status = "low"
    elif hb_g_dl > high:
        status = "high"
    else:
        status = "normal"

    return {
        "hb_g_dl": float(hb_g_dl),
        "sex": sex,
        "referenceRange": {"low": low, "high": high},
        "status": status,
        "note": "Reference ranges vary by lab, age, pregnancy status, altitude, and clinical context.",
    }

