
print("Starting import test...")
try:
    import flask
    print("Flask imported")
    import flask_cors
    print("Flask CORS imported")
    import numpy
    print("Numpy imported")
    import PIL
    print("Pillow imported")
    import cv2
    print("OpenCV imported")
    import tensorflow
    print("TensorFlow imported")
    import pymongo
    print("PyMongo imported")
    print("All imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
