from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _resolve_file_path(env_var: str, default_filename: str) -> str:
    val = os.getenv(env_var)
    if val and os.path.exists(val):
        return val
    bundled = os.path.abspath(os.path.join(os.path.dirname(__file__), default_filename))
    if os.path.exists(bundled):
        return bundled
    return bundled


@dataclass(frozen=True)
class Settings:
    # Allow overriding; default to allow all origins.
    cors_origin: str = os.getenv("CORS_ORIGIN", "*")

    # Model paths (prefer TFLite for serving).
    model_tflite_path: str = _resolve_file_path("MODEL_TFLITE_PATH", "model_from_exported.tflite")
    model_keras_path: str = os.getenv("MODEL_KERAS_PATH", "")
    labels_path: str = _resolve_file_path("LABELS_PATH", "labels.json")

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
