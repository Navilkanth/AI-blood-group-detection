
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import traceback

MODEL_PATH = r"c:\Users\navin\Downloads\bd classification\Blood-Cancer-Detection-CNN-master\Blood-Cancer-Detection-CNN-master\mymodel.h5"

def check():
    print(f"Checking model at: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print("Model file does not exist!")
        return

    try:
        print("Loading model...")
        model = load_model(MODEL_PATH, compile=False)
        print("Model loaded.")
        
        # Create a dummy image
        img = np.zeros((1, 150, 150, 3), dtype=np.float32)
        
        print("Running prediction...")
        preds = model.predict(img)
        print(f"Prediction successful: {preds}")
    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    check()
