from __future__ import annotations

from typing import Any


def ethics_safety_note() -> dict[str, Any]:
    return {
        "disclaimer": (
            "AI-assisted preliminary screening only. Do not use as a sole basis for medical decisions. "
            "Always confirm blood group with a certified laboratory test."
        ),
        "privacy": "Images are processed by the server only for inference; store only if you explicitly enable logging.",
    }

