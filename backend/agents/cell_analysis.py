from __future__ import annotations

import base64
import io
from typing import Any

import cv2
import numpy as np
from PIL import Image


def _png_base64(rgb_uint8: np.ndarray) -> str:
    img = Image.fromarray(rgb_uint8, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def analyze_cells(rgb_uint8: np.ndarray, *, return_overlay: bool = True) -> dict[str, Any]:
    """
    Very rough CV-based estimation for demo purposes:
    - RBC: circle detection
    - WBC: purple-ish pixel clustering

    This is NOT clinically accurate and depends heavily on microscope settings/stain.
    """
    bgr = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # RBC circles
    g = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(
        g,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=18,
        param1=80,
        param2=28,
        minRadius=6,
        maxRadius=28,
    )
    rbc_count = int(0 if circles is None else circles.shape[1])

    # WBC purple-ish detection (HSV range heuristic)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([120, 40, 40], dtype=np.uint8)
    upper = np.array([170, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.medianBlur(mask, 7)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    wbc_candidates = [c for c in cnts if 80 <= cv2.contourArea(c) <= 5000]
    wbc_count = int(len(wbc_candidates))

    overlay_rgb = None
    if return_overlay:
        ov = rgb_uint8.copy()
        if circles is not None:
            for (x, y, r) in np.round(circles[0, :]).astype(int):
                cv2.circle(ov, (x, y), r, (0, 255, 0), 2)
        for c in wbc_candidates:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(ov, (x, y), (x + w, y + h), (255, 0, 255), 2)
        overlay_rgb = ov

    total = rbc_count + wbc_count
    rbc_pct = (rbc_count / total * 100) if total > 0 else 0
    wbc_pct = (wbc_count / total * 100) if total > 0 else 0

    out: dict[str, Any] = {
        "rbcPercentage": round(rbc_pct, 1),
        "wbcPercentage": round(wbc_pct, 1),
        "totalCells": total,
        "rbcCount": rbc_count, 
        "wbcCount": wbc_count,
        "notes": [
            "Cell levels are shown as percentages of total cells counted via CV analytics.",
            "For diagnostic accuracy, refer to a calibrated laboratory test."
        ],
    }
    if overlay_rgb is not None:
        out["overlayPngBase64"] = _png_base64(overlay_rgb)
    return out

