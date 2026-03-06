from __future__ import annotations
import datetime
import os
import sqlite3
import json
from typing import Any
from config import settings

class DatabaseManager:
    def __init__(self) -> None:
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "records.db")
        self._init_sqlite()

    def _init_sqlite(self):
        """Initialize the local SQLite database if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    data TEXT
                )
            """)

    def _ensure_connected(self) -> bool:
        # We always have SQLite as a fallback or primary for "db file" access
        return True

    def save_report(self, report_data: dict[str, Any]) -> str | None:
        try:
            report_id = report_data.get("prediction_id", str(datetime.datetime.now().timestamp()))
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Save to SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO reports (id, timestamp, data) VALUES (?, ?, ?)",
                    (report_id, timestamp, json.dumps(report_data))
                )
            return report_id
        except Exception as e:
            print(f"Error saving report to SQLite: {e}")
            return None

    def get_reports(self, limit: int = 50) -> list[dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT data FROM reports ORDER BY timestamp DESC LIMIT ?", 
                    (limit,)
                )
                reports = []
                for row in cursor:
                    reports.append(json.loads(row["data"]))
                return reports
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []

    def get_status(self) -> dict[str, Any]:
        return {
            "connected": True,
            "type": "SQLite (Local File)",
            "database": "records.db",
            "collection": "reports",
            "path": self.db_path
        }

db_manager = DatabaseManager()
