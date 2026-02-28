from __future__ import annotations

from typing import Any


def validate_medical_rules(
    *,
    quality_ok: bool,
    consensus_confidence: float,
    min_confidence: float,
) -> dict[str, Any]:
    """
    This is a safety-oriented rule layer (NOT a medical device).
    It decides whether the system should present a "tentative" result or a "retake / confirm in lab" message.
    """
    issues: list[str] = []
    allow_result = True

    if not quality_ok:
        allow_result = False
        issues.append("Image quality check failed. Retake the image under better lighting/focus.")

    if consensus_confidence < min_confidence:
        allow_result = False
        issues.append(
            f"Low confidence ({consensus_confidence:.2f}). Please retake image and confirm via lab test."
        )

    return {
        "allowResult": allow_result,
        "issues": issues,
        "note": "This is an AI-assisted preliminary screening output; laboratory confirmation is required.",
    }

