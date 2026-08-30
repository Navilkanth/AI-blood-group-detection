from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

from utils.image_io import resize_rgb


def load_labels(labels_path: str) -> list[str]:
    """
    Supports either:
    - {"A": 0, "AB": 1, ...} mapping label->index
    - ["A","AB", ...] list in index order
    """
    p = Path(labels_path)
    if not p.exists():
        for candidate in [
            Path(__file__).resolve().parent.parent / "labels.json",
            Path(__file__).resolve().parent.parent.parent / "labels.json",
            Path.cwd() / "backend" / "labels.json",
            Path.cwd() / "labels.json",
        ]:
            if candidate.exists():
                p = candidate
                break

    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [str(x) for x in data]
            if isinstance(data, dict):
                inv: dict[int, str] = {}
                for k, v in data.items():
                    inv[int(v)] = str(k)
                return [inv[i] for i in sorted(inv.keys())]
        except Exception:
            pass

    return ["A", "AB", "B", "O"]


@dataclass(frozen=True)
class ModelInfo:
    runtime: Literal["tflite", "keras"]
    input_shape: list[int]
    input_dtype: str
    output_shape: list[int]
    output_dtype: str


class TFLitePredictor:
    def __init__(self, model_path: str, labels: list[str]):
        import tensorflow as tf  # lazy import

        self._tf = tf
        self._labels = labels
        self._interpreter = tf.lite.Interpreter(model_path=model_path)
        self._interpreter.allocate_tensors()

        self._in = self._interpreter.get_input_details()[0]
        self._out = self._interpreter.get_output_details()[0]

        self.info = ModelInfo(
            runtime="tflite",
            input_shape=[int(x) for x in self._in["shape"]],
            input_dtype=np.dtype(self._in["dtype"]).name,
            output_shape=[int(x) for x in self._out["shape"]],
            output_dtype=np.dtype(self._out["dtype"]).name,
        )

    def preprocess(self, rgb_uint8: np.ndarray) -> np.ndarray:
        # Expect NHWC
        _, h, w, c = self.info.input_shape
        if c != 3:
            raise ValueError(f"Model expects {c} channels, got RGB(3).")
        resized = resize_rgb(rgb_uint8, (w, h))
        x = resized
        in_dtype = self._in["dtype"]
        if in_dtype == np.float32:
            x = x.astype(np.float32) / 255.0
        else:
            x = x.astype(in_dtype, copy=False)
        return np.expand_dims(x, axis=0)

    def predict_proba(self, rgb_uint8: np.ndarray) -> np.ndarray:
        x = self.preprocess(rgb_uint8)
        self._interpreter.set_tensor(self._in["index"], x)
        self._interpreter.invoke()
        y = self._interpreter.get_tensor(self._out["index"])
        y = np.asarray(y).reshape(-1).astype(np.float32)

        # If logits, softmax; if already probs, this is mostly no-op.
        if not np.all((y >= 0.0) & (y <= 1.0)) or abs(float(y.sum()) - 1.0) > 1e-2:
            y = self._softmax(y)
        return y

    @staticmethod
    def _softmax(z: np.ndarray) -> np.ndarray:
        z = z - float(np.max(z))
        e = np.exp(z)
        return e / float(np.sum(e) + 1e-12)

    def decode(self, proba: np.ndarray) -> dict[str, Any]:
        idx = int(np.argmax(proba))
        label = self._labels[idx] if idx < len(self._labels) else str(idx)
        probs_by_label = {
            (self._labels[i] if i < len(self._labels) else str(i)): float(proba[i])
            for i in range(int(proba.shape[0]))
        }
        return {
            "index": idx,
            "label": label,
            "confidence": float(proba[idx]),
            "probs": probs_by_label,
        }


def build_predictor(model_tflite_path: str, labels_path: str) -> tuple[TFLitePredictor, ModelInfo, list[str]]:
    labels = load_labels(labels_path)
    pred = TFLitePredictor(model_tflite_path, labels)
    return pred, pred.info, labels

