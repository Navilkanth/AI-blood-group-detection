from __future__ import annotations

from typing import Any


def assess_confidence(conf: float) -> dict[str, Any]:
    if conf >= 0.90:
        level = "very_high"
    elif conf >= 0.80:
        level = "high"
    elif conf >= 0.70:
        level = "medium"
    elif conf >= 0.60:
        level = "low"
    else:
        level = "very_low"

    return {"score": float(conf), "level": level}

