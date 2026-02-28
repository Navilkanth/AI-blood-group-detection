from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Wrap a TensorFlow SavedModel into a Keras 3 .keras file using keras.layers.TFSMLayer. "
            "This produces a .keras that deserializes on TF 2.20 / Keras 3."
        )
    )
    ap.add_argument(
        "--in-savedmodel",
        default=str(Path(__file__).resolve().parents[1] / "converted" / "saved_model"),
    )
    ap.add_argument(
        "--out-keras",
        default=str(Path(__file__).resolve().parents[1] / "converted" / "model_keras3.keras"),
    )
    ap.add_argument("--endpoint", default=os.getenv("SAVEDMODEL_ENDPOINT", "serving_default"))
    args = ap.parse_args()

    import tensorflow as tf

    print("TensorFlow:", tf.__version__)
    saved_dir = Path(args.in_savedmodel)
    out_path = Path(args.out_keras)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # The SavedModel expects float32 NHWC input, but we keep the wrapper generic.
    layer = tf.keras.layers.TFSMLayer(str(saved_dir), call_endpoint=args.endpoint)

    # Infer input signature from SavedModel.
    # We assume image classifier shape [None, 224, 224, 3] (matches your TFLite report).
    inp = tf.keras.Input(shape=(224, 224, 3), dtype=tf.float32, name="input_1")
    out = layer(inp)
    model = tf.keras.Model(inputs=inp, outputs=out, name="blood_group_model_keras3")

    print("Saving Keras 3 model to:", out_path)
    model.save(str(out_path))
    print("Done.")


if __name__ == "__main__":
    main()

