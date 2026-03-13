
import os
import numpy as np
import tensorflow as tf
import keras
from keras import layers
import traceback

MODEL_PATH = r"c:\Users\navin\Downloads\bd classification\Blood-Cancer-Detection-CNN-master\Blood-Cancer-Detection-CNN-master\mymodel.h5"

def create_model():
    # Recreate the exact architecture from the notebook
    # Setting channels_first causes standard Keras to interpret the 1st dim as channels
    model = keras.Sequential([
        layers.Input(shape=(150, 150, 3)), 
        layers.Conv2D(16, (3, 3), activation='relu', padding="same"),
        layers.Conv2D(16, (3, 3), padding="same", activation='relu'),
        layers.Conv2D(32, (3, 3), activation='relu', padding="same"),
        layers.Conv2D(32, (3, 3), padding="same", activation='relu"),
        layers.Conv2D(64, (3, 3), activation='relu', padding="same"),
        layers.Conv2D(64, (3, 3), padding="same", activation='relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(2, activation='sigmoid')
    ])
    return model

def test_load():
    try:
        # 1. Try to load the model normally first, but with a trick
        print("Attempting to load model with compile=False...")
        # Sometimes setting the backend explicitly helps
        os.environ['KERAS_BACKEND'] = 'tensorflow'
        
        # Try to resolve the groups issue by defining image_data_format
        keras.backend.set_image_data_format('channels_first')
        
        try:
            model = keras.models.load_model(MODEL_PATH, compile=False)
            print("Successfully loaded model via load_model!")
            model.summary()
        except Exception as e:
            print(f"Standard load_model failed: {e}")
            print("Attempting manual reconstruction and weights load...")
            model = create_model()
            model.load_weights(MODEL_PATH)
            print("Successfully loaded weights into manual model!")
            model.summary()
            
        # Test prediction
        dummy_input = np.zeros((1, 150, 150, 3))
        pred = model.predict(dummy_input, verbose=0)
        print(f"Prediction test success: {pred.shape}")
        
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
