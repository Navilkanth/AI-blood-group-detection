import sys
import os

# Ensure backend directory is in Python path for submodules
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the Flask application instance from backend/app.py
from backend.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
