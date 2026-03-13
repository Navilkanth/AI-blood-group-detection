
import tensorflow as tf
import os

model_path = r"c:\Users\navin\Downloads\bd classification\backend\model_from_exported.tflite"
if not os.path.exists(model_path):
    print(f"File not found: {model_path}")
else:
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    output_details = interpreter.get_output_details()
    print(f"Output details: {output_details}")
    print(f"Output shape: {output_details[0]['shape']}")
