import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
from tensorflow.keras.preprocessing import image
import os

# Load model lazily
_model = None
DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Blood-Cancer-Detection-CNN-master", "Blood-Cancer-Detection-CNN-master", "mymodel.h5")
)
MODEL_PATH = os.getenv("CANCER_MODEL_PATH", DEFAULT_MODEL_PATH)

def create_legacy_model():
    """
    Manually reconstruct the model architecture from the notebook.
    The original model was trained with Keras 2 'th' ordering (Channels First).
    Due to a mismatch during training, the shape was (C=150, H=150, W=3).
    """
    model = keras.Sequential([
        layers.Input(shape=(150, 150, 3)), # Interpreted as (C, H, W)
        layers.Conv2D(16, (3, 3), activation='relu', padding="same", data_format='channels_first'),
        layers.Conv2D(16, (3, 3), padding="same", activation='relu', data_format='channels_first'),
        layers.Conv2D(32, (3, 3), activation='relu', padding="same", data_format='channels_first'),
        layers.Conv2D(32, (3, 3), padding="same", activation='relu', data_format='channels_first'),
        layers.Conv2D(64, (3, 3), activation='relu', padding="same", data_format='channels_first'),
        layers.Conv2D(64, (3, 3), padding="same", activation='relu', data_format='channels_first'),
        layers.MaxPooling2D(pool_size=(2, 2), data_format='channels_first'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(2, activation='sigmoid')
    ])
    return model

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Cancer model not found at {MODEL_PATH}")
        
        try:
            # Reconstruct model and load weights to avoid Keras 3 deserialization bugs
            _model = create_legacy_model()
            _model.load_weights(MODEL_PATH)
        except Exception as e:
            # Fallback to standard load if manual fails
            try:
                _model = keras.models.load_model(MODEL_PATH, compile=False)
            except:
                raise RuntimeError(f"Failed to load cancer model: {e}")
                
    return _model

def predict_cancer(img_path):
    """
    Predict blood cancer from cell image.
    Uses a manual model reconstruction for Keras 3 compatibility.
    """
    model = get_model()
    
    # Preprocessing
    img = image.load_img(img_path, target_size=(150, 150))
    x = image.img_to_array(img)
    
    # The original shape was (C=150, H=150, W=3) due to a training mismatch.
    # We provide exactly this shape (Batch, 150, 150, 3) with channels_first.
    x = np.expand_dims(x, axis=0)
    x = x / 255.0 
    
    # Prediction
    try:
        preds = model.predict(x, verbose=0)
        if hasattr(preds, 'numpy'):
            preds = preds.numpy()
    except Exception as e:
        raise RuntimeError(f"Model prediction failed: {e}")
    
    if preds is None or len(preds) == 0:
        raise ValueError("Model returned empty prediction")

    classes = ["Normal", "Cancer"]
    
    # Handle both binary (1 output) and categorical (2 outputs)
    if len(preds[0]) > 1:
        class_idx = np.argmax(preds[0])
        confidence = float(preds[0][class_idx])
    else:
        prob_cancer = float(preds[0][0])
        if prob_cancer > 0.5:
            class_idx = 1
            confidence = prob_cancer
        else:
            class_idx = 0
            confidence = 1 - prob_cancer
            
    label = classes[class_idx]
    
    return {
        "label": label,
        "confidence": confidence,
        "raw_scores": preds[0].tolist()
    }
