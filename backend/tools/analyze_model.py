from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def analyze_tflite(path: str) -> dict[str, Any]:
    import tensorflow as tf
    import numpy as np

    intr = tf.lite.Interpreter(model_path=path)
    intr.allocate_tensors()
    inputs = intr.get_input_details()
    outputs = intr.get_output_details()

    def to_jsonable(v: Any) -> Any:
        if isinstance(v, np.ndarray):
            return v.tolist()
        if isinstance(v, (np.integer, np.floating)):
            return v.item()
        if isinstance(v, dict):
            return {str(k): to_jsonable(val) for k, val in v.items()}
        if isinstance(v, (list, tuple)):
            return [to_jsonable(x) for x in v]
        if isinstance(v, type):
            return getattr(v, "__name__", str(v))
        return v

    def simplify(details: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [to_jsonable(d) for d in details]  # type: ignore[return-value]

    return {
        "path": path,
        "inputs": simplify(inputs),
        "outputs": simplify(outputs),
    }


def analyze_keras(path: str) -> dict[str, Any]:
    import tensorflow as tf

    m = tf.keras.models.load_model(path, compile=False)
    # Capture a minimal JSON-friendly view (full summary is printed separately)
    return {
        "path": path,
        "tf_version": tf.__version__,
        "inputs": [(t.name, [int(x) if x is not None else None for x in t.shape], t.dtype.name) for t in m.inputs],
        "outputs": [(t.name, [int(x) if x is not None else None for x in t.shape], t.dtype.name) for t in m.outputs],
        "params": int(m.count_params()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--tflite",
        default=os.getenv("MODEL_TFLITE_PATH", r"C:\Users\navin\Downloads\blood_group_model.tflite"),
    )
    ap.add_argument(
        "--keras",
        default=os.getenv("MODEL_KERAS_PATH", r"C:\Users\navin\Downloads\blood_group_model (1).keras"),
    )
    ap.add_argument(
        "--labels",
        default=os.getenv("LABELS_PATH", r"C:\Users\navin\Downloads\labels (2).json"),
    )
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "model_report.json"))
    args = ap.parse_args()

    report: dict[str, Any] = {}

    try:
        import tensorflow as tf

        report["tensorflow_version"] = tf.__version__
    except Exception as e:
        report["tensorflow_import_error"] = str(e)

    if args.labels and Path(args.labels).exists():
        report["labels_path"] = args.labels
        report["labels_raw"] = json.loads(Path(args.labels).read_text(encoding="utf-8"))

    if args.tflite and Path(args.tflite).exists():
        report["tflite"] = analyze_tflite(args.tflite)

    if args.keras and Path(args.keras).exists():
        try:
            report["keras"] = analyze_keras(args.keras)
        except Exception as e:
            report["keras_error"] = str(e)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")

    if "keras" in report:
        # Print human-friendly summary to stdout (best-effort)
        try:
            import tensorflow as tf

            m = tf.keras.models.load_model(args.keras, compile=False)
            m.summary()
        except Exception:
            pass


if __name__ == "__main__":
    main()

