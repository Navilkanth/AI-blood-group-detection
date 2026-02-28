from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

from agents.cell_analysis import analyze_cells
from agents.confidence import assess_confidence
from agents.consensus import build_votes, consensus_from_votes, votes_to_dict
from agents.ethics import ethics_safety_note
from agents.hemoglobin import check_hemoglobin
from agents.image_quality import assess_image_quality, to_dict as quality_to_dict
from agents.medical_rules import validate_medical_rules
from agents.model_runtime import build_predictor
from config import settings
from utils.image_io import decode_image_bytes
from utils.mongodb import db_manager


app = Flask(__name__)
# Enable CORS for the specific origins used in development
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]}})

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    print("!!! SERVER ERROR !!!")
    traceback.print_exc()
    return jsonify({
        "error": str(e),
        "type": e.__class__.__name__,
        "traceback": traceback.format_exc() if app.debug else None
    }), 500


_predictor = None
_model_info = None
_labels: list[str] | None = None


def _ensure_model_loaded() -> None:
    global _predictor, _model_info, _labels
    if _predictor is not None:
        return
    if not os.path.exists(settings.model_tflite_path):
        raise FileNotFoundError(
            f"TFLite model not found at MODEL_TFLITE_PATH={settings.model_tflite_path}"
        )
    if not os.path.exists(settings.labels_path):
        raise FileNotFoundError(f"Labels not found at LABELS_PATH={settings.labels_path}")

    _predictor, _model_info, _labels = build_predictor(
        settings.model_tflite_path, settings.labels_path
    )


@app.get("/api/health")
def health() -> Any:
    return jsonify({"ok": True})


@app.get("/api/model")
def model_info() -> Any:
    try:
        _ensure_model_loaded()
        assert _model_info is not None
        assert _labels is not None
        return jsonify({"loaded": True, "model": _model_info.__dict__, "labels": _labels})
    except Exception as e:
        return jsonify({"loaded": False, "error": str(e)}), 500


@app.post("/api/predict/blood-group")
def predict_blood_group() -> Any:
    _ensure_model_loaded()
    assert _predictor is not None
    assert _labels is not None
    assert _model_info is not None

    if "image" not in request.files:
        return jsonify({"error": "Missing multipart file field 'image'."}), 400

    image_bytes = request.files["image"].read()
    decoded = decode_image_bytes(image_bytes)

    quality = assess_image_quality(decoded.rgb)
    quality_dict = quality_to_dict(quality)

    votes = build_votes(decoded.rgb, _predictor.predict_proba, _labels)
    consensus = consensus_from_votes(votes, _labels)

    rules = validate_medical_rules(
        quality_ok=quality.ok,
        consensus_confidence=float(consensus["confidence"]),
        min_confidence=settings.min_confidence,
    )

    confidence = assess_confidence(float(consensus["confidence"]))

    response: dict[str, Any] = {
        "prediction": {
            "label": consensus["label"],
            "index": consensus["index"],
            "confidence": consensus["confidence"],
            "probs": consensus["meanProbs"],
        },
        "agents": {
            "imageQuality": quality_dict,
            "visionVotes": votes_to_dict(votes),
            "consensus": {
                "stabilityStd": consensus["stabilityStd"],
            },
            "medicalRules": rules,
            "confidenceAssessment": confidence,
            "ethicsSafety": ethics_safety_note(),
        },
        "image": {"width": decoded.width, "height": decoded.height},
        "model": _model_info.__dict__,
        "explainable": {
            "summary": (
                f"Consensus vote predicts {consensus['label']} with confidence {consensus['confidence']:.2f}. "
                + ("Result allowed." if rules["allowResult"] else "Result blocked: " + "; ".join(rules["issues"]))
            )
        },
    }

    # Always return 200 with a 'blocked' flag instead of HTTP 422,
    # so the frontend can still display the AI output.
    response["blocked"] = bool(
        (settings.min_quality_ok and not quality.ok) or (not rules["allowResult"])
    )

    # Persistence: Save to MongoDB if configured
    try:
        db_id = db_manager.save_report(response)
        if db_id:
            response["db_id"] = db_id
    except Exception as e:
        print(f"Non-blocking persistence error: {e}")

    return jsonify(response)


@app.post("/api/check/hemoglobin")
def hemoglobin_endpoint() -> Any:
    data = request.get_json(silent=True) or {}
    try:
        hb = float(data.get("hb_g_dl"))
        sex = str(data.get("sex", "other")).lower()
        if sex not in {"male", "female", "other"}:
            sex = "other"
        return jsonify(check_hemoglobin(hb, sex))  # type: ignore[arg-type]
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/analyze/cells")
def cells_endpoint() -> Any:
    if "image" not in request.files:
        return jsonify({"error": "Missing multipart file field 'image'."}), 400
    image_bytes = request.files["image"].read()
    decoded = decode_image_bytes(image_bytes)
    return jsonify(analyze_cells(decoded.rgb, return_overlay=True))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)

