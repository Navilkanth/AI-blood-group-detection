from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import cv2
import numpy as np


@dataclass(frozen=True)
class Vote:
    agent: str
    probs: list[float]
    label: str
    confidence: float


def _rotate(rgb: np.ndarray, degrees: float) -> np.ndarray:
    h, w = rgb.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), degrees, 1.0)
    return cv2.warpAffine(rgb, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def _center_crop(rgb: np.ndarray, frac: float) -> np.ndarray:
    h, w = rgb.shape[:2]
    ch, cw = int(h * frac), int(w * frac)
    y0 = (h - ch) // 2
    x0 = (w - cw) // 2
    cropped = rgb[y0 : y0 + ch, x0 : x0 + cw]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def build_votes(
    rgb_uint8: np.ndarray,
    predict_proba: Callable[[np.ndarray], np.ndarray],
    labels: list[str],
) -> list[Vote]:
    variants: list[tuple[str, np.ndarray]] = [
        ("base", rgb_uint8),
        ("flip_h", np.ascontiguousarray(rgb_uint8[:, ::-1, :])),
        ("rot_-6", _rotate(rgb_uint8, -6.0)),
        ("rot_+6", _rotate(rgb_uint8, +6.0)),
        ("crop_0.85", _center_crop(rgb_uint8, 0.85)),
    ]

    votes: list[Vote] = []
    for name, v in variants:
        p = predict_proba(v).astype(np.float32).reshape(-1)
        idx = int(np.argmax(p))
        label = labels[idx] if idx < len(labels) else str(idx)
        votes.append(
            Vote(
                agent=f"vision_{name}",
                probs=[float(x) for x in p.tolist()],
                label=label,
                confidence=float(p[idx]),
            )
        )
    return votes


def consensus_from_votes(votes: list[Vote], labels: list[str]) -> dict[str, Any]:
    if not votes:
        raise ValueError("No votes to aggregate")

    probs = np.array([v.probs for v in votes], dtype=np.float32)
    mean = probs.mean(axis=0)
    std = probs.std(axis=0)

    idx = int(np.argmax(mean))
    label = labels[idx] if idx < len(labels) else str(idx)
    return {
        "label": label,
        "index": idx,
        "confidence": float(mean[idx]),
        "meanProbs": {
            (labels[i] if i < len(labels) else str(i)): float(mean[i])
            for i in range(int(mean.shape[0]))
        },
        "stabilityStd": {
            (labels[i] if i < len(labels) else str(i)): float(std[i])
            for i in range(int(std.shape[0]))
        },
    }


def votes_to_dict(votes: list[Vote]) -> list[dict[str, Any]]:
    return [
        {
            "agent": v.agent,
            "label": v.label,
            "confidence": v.confidence,
            "probs": v.probs,
        }
        for v in votes
    ]

