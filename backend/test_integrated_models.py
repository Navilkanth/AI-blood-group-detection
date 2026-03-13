
import os
import sys

# Paths to models
malaria_path = r"c:\Users\navin\Downloads\bd classification\Malaria-master\Malaria-master\model.h5"
cancer_path = r"c:\Users\navin\Downloads\bd classification\Blood-Cancer-Detection-CNN-master\Blood-Cancer-Detection-CNN-master\mymodel.h5"

print(f"Malaria model exists: {os.path.exists(malaria_path)}")
print(f"Cancer model exists: {os.path.exists(cancer_path)}")

try:
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
except ImportError:
    print("TensorFlow not installed")
    sys.exit(1)

from tensorflow.keras.models import load_model

print("Loading Malaria model...")
try:
    m = load_model(malaria_path)
    print("Malaria model loaded successfully")
except Exception as e:
    print(f"Error loading Malaria model: {e}")

print("Loading Cancer model...")
try:
    # Use compile=False as in the agent code
    c = load_model(cancer_path, compile=False)
    print("Cancer model loaded successfully")
except Exception as e:
    print(f"Error loading Cancer model: {e}")
