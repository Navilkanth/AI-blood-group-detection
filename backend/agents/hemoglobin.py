from __future__ import annotations

from typing import Any, Literal


Sex = Literal["male", "female", "other"]


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

