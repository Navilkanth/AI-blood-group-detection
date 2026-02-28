from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Loads a legacy Keras v2 .keras model and exports a TensorFlow SavedModel "
            "for compatibility with newer Keras via TFSMLayer."
        )
    )
    ap.add_argument(
        "--in-keras",
        default=os.getenv("MODEL_KERAS_PATH", r"C:\Users\navin\Downloads\blood_group_model (1).keras"),
    )
    ap.add_argument(
        "--out-savedmodel",
        default=str(Path(__file__).resolve().parents[1] / "converted" / "saved_model"),
    )
    args = ap.parse_args()

    in_path = Path(args.in_keras)
    out_dir = Path(args.out_savedmodel)
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    import tensorflow as tf

    print("TensorFlow:", tf.__version__)
    print("Loading:", in_path)
    model = tf.keras.models.load_model(str(in_path), compile=False)

    # Export SavedModel (directory)
    print("Exporting SavedModel to:", out_dir)
    # In TF/Keras v2, model.save(dir) writes SavedModel by default.
    model.save(str(out_dir))

    print("Done.")


if __name__ == "__main__":
    main()

