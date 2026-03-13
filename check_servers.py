
import requests
import time

def check_server(url):
    try:
        response = requests.get(url, timeout=5)
        print(f"Status of {url}: {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to connect to {url}: {e}")
        return False

# Give it some time to start
time.sleep(5)

print("Checking backend...")
check_server("http://localhost:5000/api/health")

print("Checking frontend...")
check_server("http://localhost:5173")
