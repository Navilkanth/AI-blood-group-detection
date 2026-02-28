from __future__ import annotations
import datetime
import os
from typing import Any
from config import settings

class MongoDBManager:
    def __init__(self) -> None:
        self._client: Any = None
        self._db: Any = None
        self._collection: Any = None
        self._initialized = False

    def _ensure_connected(self) -> bool:
        if not settings.mongo_uri or settings.mongo_uri.strip() == "":
            return False
            
        if self._initialized:
            return True

        try:
            from pymongo import MongoClient
            self._client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
            self._db = self._client[settings.mongo_db_name]
            self._collection = self._db[settings.mongo_collection_name]
            # Try a ping to verify connection
            self._client.admin.command('ping')
            self._initialized = True
            print("Successfully connected to MongoDB Atlas.")
            return True
        except ImportError:
            print("MongoDB error: 'pymongo' library not found. Please run: pip install pymongo dnspython")
            return False
        except Exception as e:
            print(f"Failed to connect to MongoDB Atlas: {e}")
            return False

    def save_report(self, report_data: dict[str, Any]) -> str | None:
        if not self._ensure_connected():
            return None

        try:
            document = {
                **report_data,
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
            }
            # Clean up potentially non-serializable objects (like numpy arrays)
            # This is a precaution if response contains raw arrays
            result = self._collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving report to MongoDB: {e}")
            return None

    def get_reports(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._ensure_connected():
            return []

        try:
            # Sort by timestamp descending
            cursor = self._collection.find().sort("timestamp", -1).limit(limit)
            reports = []
            for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                # Convert datetime to ISO format
                if "timestamp" in doc and isinstance(doc["timestamp"], datetime.datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                reports.append(doc)
            return reports
        except Exception as e:
            print(f"Error fetching reports from MongoDB: {e}")
            return []

db_manager = MongoDBManager()
