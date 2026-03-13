
import os
import sys
# Add current directory to path
sys.path.append(os.getcwd())

from agents.cancer_detection import predict_cancer
import numpy as np
from PIL import Image

def test():
    print("Testing Cancer Prediction Agent...")
    test_img = "test_cell.png"
    # Create a dummy image
    img = Image.new('RGB', (150, 150), color=(73, 109, 137))
    img.save(test_img)
    
    try:
        result = predict_cancer(test_img)
        print("Result:", result)
    except Exception as e:
        print("Error during prediction:")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(test_img):
            os.remove(test_img)

if __name__ == "__main__":
    test()
