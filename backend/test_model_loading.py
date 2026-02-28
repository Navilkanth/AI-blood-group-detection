
import os
import sys

# Add current dir to path to import agents
sys.path.append(os.path.dirname(__file__))

try:
    from config import settings
    from agents.model_runtime import build_predictor
    
    print(f"Checking model at: {settings.model_tflite_path}")
    print(f"Checking labels at: {settings.labels_path}")
    
    if not os.path.exists(settings.model_tflite_path):
        print("ERROR: Model file not found!")
    if not os.path.exists(settings.labels_path):
        print("ERROR: Labels file not found!")
        
    predictor, info, labels = build_predictor(settings.model_tflite_path, settings.labels_path)
    print("SUCCESS: Model and labels loaded successfully.")
    print(f"Model Info: {info}")
    print(f"Labels: {labels}")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
