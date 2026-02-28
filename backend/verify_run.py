
import os
import sys
import numpy as np

# Add current dir to path to import agents
sys.path.append(os.path.dirname(__file__))

try:
    from config import settings
    from agents.model_runtime import build_predictor
    
    print(f"Loading model from: {settings.model_tflite_path}")
    predictor, info, labels = build_predictor(settings.model_tflite_path, settings.labels_path)
    print("SUCCESS: Model loaded.")
    
    # Create dummy input (224x224x3)
    dummy_input = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    print("Running dummy prediction...")
    proba = predictor.predict_proba(dummy_input)
    result = predictor.decode(proba)
    
    print(f"Prediction result: {result}")
    print("STATUS: RUNNING")
except Exception as e:
    print(f"STATUS: NOT RUNNING")
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
