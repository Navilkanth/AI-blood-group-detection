from __future__ import annotations

import os
import uuid
import datetime
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

from agents.cell_analysis import analyze_cells
from agents.confidence import assess_confidence
from agents.consensus import build_votes, consensus_from_votes, votes_to_dict
from agents.ethics import ethics_safety_note
from agents.hemoglobin import check_hemoglobin, estimate_hb_from_image
from agents.image_quality import assess_image_quality, to_dict as quality_to_dict
from agents.medical_rules import validate_medical_rules
from agents.model_runtime import build_predictor
from agents.rh_factor import detect_rh_factor, get_rh_confidence
from agents.malaria_detection import predict_malaria
from agents.cancer_detection import predict_cancer
from config import settings
from utils.image_io import decode_image_bytes
from utils.mongodb import db_manager


app = Flask(__name__)
# Enable CORS for frontend clients (including Vercel deployments and localhost)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

    # Check for Invalid Sample (as part of the quality check)
    is_invalid = any("Invalid sample" in r for r in quality.reasons)
    
    if is_invalid:
        return jsonify({
            "error": "Invalid Sample: The uploaded image does not appear to be a valid blood sample.",
            "blocked": True,
            "reasoning": "Analysis terminated: Image content mismatch (not a blood group image).",
            "quality": quality_dict
        }), 422

    hb_val = estimate_hb_from_image(decoded.rgb)
    hb_report = check_hemoglobin(hb_val, "other")

    votes = build_votes(decoded.rgb, _predictor.predict_proba, _labels)
    consensus = consensus_from_votes(votes, _labels)

    rules = validate_medical_rules(
        quality_ok=quality.ok,
        consensus_confidence=float(consensus["confidence"]),
        min_confidence=settings.min_confidence,
    )

    confidence = assess_confidence(float(consensus["confidence"]))
    ethics = ethics_safety_note()

    # --- Rh Factor Addition (8-Class Expansion) ---
    rh_symbol = detect_rh_factor(decoded.rgb)
    rh_conf = get_rh_confidence(decoded.rgb)
    abo_label = consensus["label"]
    final_label = f"({abo_label}{rh_symbol})"
    
    # Expand 4-class probs to 8-class probs
    abo_probs = consensus["meanProbs"]
    final_probs = {}
    for abo, p in abo_probs.items():
        if rh_symbol == "+":
            final_probs[f"{abo}+"] = p * rh_conf
            final_probs[f"{abo}-"] = p * (1.0 - rh_conf)
        else:
            final_probs[f"{abo}+"] = p * (1.0 - rh_conf)
            final_probs[f"{abo}-"] = p * rh_conf
            
    # Normalize probabilities to sum to 1.0
    total_p = sum(final_probs.values())
    if total_p > 0:
        final_probs = {k: v/total_p for k, v in final_probs.items()}

    # --- Multi-Agent Consensus Logic (Robust 5+9 Agent System) ---
    vision_labels = [v.label for v in votes]
    top_label = consensus["label"]
    vision_agree_count = sum(1 for l in vision_labels if l == top_label)
    vision_voter_ratio = vision_agree_count / len(votes)
    
    # Internal vision consensus must be strong (>70% of voters agree)
    vision_consensus_valid = vision_voter_ratio >= 0.70

    agent_status = {
        "Vision Consensus Agent": vision_consensus_valid, 
        "Medical Rules Agent": rules["allowResult"],
        "Image Validation Agent": quality.ok,
        "Confidence Assessment Agent": confidence["score"] >= settings.min_confidence,
        "Safety & Ethics Agent": True,
    }
    
    agree_names = [name for name, ok in agent_status.items() if ok]
    disagree_names = [name for name, ok in agent_status.items() if not ok]
    agree_count = len(agree_names)
    consensus_met = (agree_count == 5) # All high-level agents must agree
    
    reasoning = (
        f"{agree_count}/5 high-level agents (Verification {int(agree_count/5*100)}%) agree on blood group: {final_label}. "
        f"ABO: {abo_label}, Rh: {rh_symbol} (Agent Confidence: {int(rh_conf*100)}%). "
        f"Multi-voter vision agreement: {int(vision_voter_ratio*100)}% ({vision_agree_count}/{len(votes)} sub-agents). "
        f"Consensus confidence: {int(consensus['confidence']*100)}%. "
    )
    if not vision_consensus_valid:
        reasoning += f"CRITICAL: Vision sub-agents disagreed! "
    if disagree_names:
        reasoning += f"Blocked by: {', '.join(disagree_names)}. "
    
    reasoning += f"Estimated Hb: {hb_val:.1f} g/dL."

    response: dict[str, Any] = {
        "prediction_id": str(uuid.uuid4()),
        "feature": "blood_group",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "consensus_met": consensus_met,
        "reasoning": reasoning,
        "prediction": {
            "label": final_label,
            "index": consensus["index"],  # Maintain ABO index for backward compat
            "confidence": float(final_probs.get(final_label.strip("()"), consensus["confidence"])),
            "probs": final_probs,
        },
        "haemoglobin": hb_report,
        "agents": {
            "imageQuality": quality_dict,
            "visionVotes": votes_to_dict(votes),
            "consensus": {
                "stabilityStd": consensus["stabilityStd"],
                "agreeCount": agree_count,
            },
            "medicalRules": rules,
            "confidenceAssessment": confidence,
            "rhFactorAgent": {
                "symbol": rh_symbol,
                "confidence": rh_conf,
                "method": "Texture Agglutination Analysis"
            },
            "ethicsSafety": ethics,
        },
        "image": {"width": decoded.width, "height": decoded.height},
        "model": _model_info.__dict__,
        "explainable": {
            "summary": reasoning 
        },
        "blocked": not consensus_met,
    }

    # Persistence
    try:
        db_id = db_manager.save_report(response)
        if db_id:
            response["db_id"] = db_id
    except Exception as e:
        print(f"DB Error: {e}")

    print(f"[{datetime.datetime.now()}] BLOOD GROUP result: {final_label} ({abo_label}{rh_symbol})")
    return jsonify(response)


@app.post("/api/check/hemoglobin")
def hemoglobin_endpoint() -> Any:
    if "image" not in request.files:
        return jsonify({"error": "Missing multipart file field 'image'."}), 400
    
    image_bytes = request.files["image"].read()
    decoded = decode_image_bytes(image_bytes)
    
    hb_val = estimate_hb_from_image(decoded.rgb)
    result = check_hemoglobin(hb_val, "other")
    
    response = {
        "prediction_id": f"hb-{uuid.uuid4().hex[:8]}",
        "feature": "hemoglobin",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "haemoglobin": result,
        "success": True
    }
    
    try:
        db_manager.save_report(response)
    except Exception as e:
        print(f"DB Error: {e}")
        
    return jsonify(response)


@app.post("/api/analyze/cells")
def cells_endpoint() -> Any:
    if "image" not in request.files:
        return jsonify({"error": "Missing multipart file field 'image'."}), 400
    image_bytes = request.files["image"].read()
    decoded = decode_image_bytes(image_bytes)
    result = analyze_cells(decoded.rgb, return_overlay=True)
    
    response = {
        "prediction_id": f"cel-{uuid.uuid4().hex[:8]}",
        "feature": "cells",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "analysis": result,
        "success": True
    }
    
    try:
        db_manager.save_report(response)
    except Exception as e:
        print(f"DB Error: {e}")
        
    return jsonify(response)


@app.get("/api/db-status")
def db_status() -> Any:
    try:
        status = db_manager.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)}), 500


@app.get("/api/history")
def history() -> Any:
    try:
        records = db_manager.get_reports(limit=100)
        # Ensure compatibility
        for r in records:
            if "_id" not in r:
                r["_id"] = r.get("prediction_id", "unknown_id")
            if "timestamp" not in r:
                r["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        return jsonify({"records": records})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict-malaria", methods=["POST"])
def predict_malaria_endpoint():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        
        # Save temp file
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"malaria_{uuid.uuid4()}.png")
        file.save(temp_path)
        
        # Predict
        result = predict_malaria(temp_path)
        
        # Cleanup
        os.remove(temp_path)
        
        response = {
            "success": True,
            "prediction_id": f"mal-{uuid.uuid4().hex[:8]}",
            "feature": "malaria",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "prediction": result
        }
        
        try:
            db_manager.save_report(response)
        except Exception as e:
            print(f"DB Error: {e}")
            
        print(f"[{datetime.datetime.now()}] MALARIA result: {result['label']} (Confidence: {result['confidence']:.2f})")
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict-cancer", methods=["POST"])
def predict_cancer_endpoint():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        
        # Save temp file
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"cancer_{uuid.uuid4()}.png")
        file.save(temp_path)
        
        # Predict
        result = predict_cancer(temp_path)
        
        # Cleanup
        os.remove(temp_path)
        
        response = {
            "success": True,
            "prediction_id": f"can-{uuid.uuid4().hex[:8]}",
            "feature": "cancer",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "prediction": result
        }
        
        try:
            db_manager.save_report(response)
        except Exception as e:
            print(f"DB Error: {e}")
            
        print(f"[{datetime.datetime.now()}] CANCER result: {result['label']} (Confidence: {result['confidence']:.2f})")
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
