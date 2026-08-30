import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# Load model lazily to save memory during startup
_model = None
DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Malaria-master", "Malaria-master", "model.h5")
)
MODEL_PATH = os.getenv("MALARIA_MODEL_PATH", DEFAULT_MODEL_PATH)

def get_model():
    global _model
    if _model is None:
        _model = load_model(MODEL_PATH)
    return _model

def predict_malaria(img_path):
    """
    Predict malaria from cell image.
    Target size: 100x100
    Classes: ["Parasitized", "Uninfected"]
    """
    model = get_model()
    
    # Preprocessing
    img = image.load_img(img_path, target_size=(100, 100))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.
    
    # Prediction
    try:
        preds = model.predict(img_tensor, verbose=0)
        if hasattr(preds, 'numpy'):
            preds = preds.numpy()
    except Exception as e:
        raise RuntimeError(f"Malaria model prediction failed: {e}")
    # Binary classification usually returns probability of class 1 (Uninfected) or 
    # if it's 2 output neurons: [p0, p1]
    
    classes = ["Parasitized", "Uninfected"]
    
    if len(preds[0]) > 1:
        class_idx = np.argmax(preds[0])
        confidence = float(preds[0][class_idx])
    else:
        # Assuming sigmoid output for 2nd class (Uninfected)
        prob_uninfected = float(preds[0][0])
        if prob_uninfected > 0.5:
            class_idx = 1
            confidence = prob_uninfected
        else:
            class_idx = 0
            confidence = 1 - prob_uninfected
            
    label = classes[class_idx]
    
    return {
        "label": label,
        "confidence": confidence,
        "raw_scores": preds[0].tolist()
    }
