
import requests
import json

url = "http://localhost:5000/api/predict/blood-group"
image_path = r"C:\Users\navin\.gemini\antigravity\brain\8abe84f0-8c70-44ed-ad90-3a8e138ff891\test_blood_sample_1773296187226.png"

with open(image_path, "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files)

print(f"Status: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)
