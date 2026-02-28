from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Allow overriding; default to allow all origins (dev only).
    cors_origin: str = os.getenv("CORS_ORIGIN", "*")

    # Model paths (prefer TFLite for serving).
    model_tflite_path: str = os.getenv(
        "MODEL_TFLITE_PATH",
        # New TFLite exported from C:\Users\navin\Downloads\exported_model\exported_model
        os.path.join(os.path.dirname(__file__), "model_from_exported.tflite"),
    )
    model_keras_path: str = os.getenv(
        "MODEL_KERAS_PATH", r"C:\Users\navin\Downloads\blood_group_model (1).keras"
    )
    labels_path: str = os.getenv("LABELS_PATH", r"C:\Users\navin\Downloads\labels (2).json")

    # Prediction behavior
    # For the demo UI, do not hard-block low quality images.
    min_quality_ok: bool = os.getenv("REQUIRE_QUALITY_OK", "false").lower() == "true"
    # Allow very low confidence; the frontend will still see probabilities.
    min_confidence: float = float(os.getenv("MIN_CONFIDENCE", "0.10"))

    # MongoDB configuration
    mongo_uri: str | None = os.getenv("MONGO_URI")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "blood_group_db")
    mongo_collection_name: str = os.getenv("MONGO_COLLECTION_NAME", "reports")


settings = Settings()
