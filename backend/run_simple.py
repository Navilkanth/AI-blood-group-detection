
import os
print("SCRIPT START")
import flask
print("FLASK LOADED")
from app import app
print("APP IMPORTED")
if __name__ == "__main__":
    print("RUNNING APP")
    app.run(port=5000)
