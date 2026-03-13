
import requests
import os

url = "http://localhost:5000/api/predict-cancer"
# Just use any small image file from the project 
img_path = r"c:\Users\navin\Downloads\bd classification\Malaria-master\Malaria-master\demo\Malaria-cell-sample.png"

def trigger():
    if not os.path.exists(img_path):
        print(f"Test image not found at {img_path}")
        return

    try:
        with open(img_path, 'rb') as f:
            files = {'image': ('test.png', f, 'image/png')}
            print("Sending request...")
            response = requests.post(url, files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger()
