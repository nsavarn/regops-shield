import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

load_dotenv()


class MongoUtils:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client["regops_shield"]
        self.sessions = self.db["shadow_sessions"]
        self.policies_col = self.db["policies"]
        # Ensure text index on policies for keyword retrieval
        self.policies_col.create_index([("text", "text")], default_language="english")

    def save_session(self, session_data: dict) -> str:
        """Persist a ShadowRunSession document and return its MongoDB ID."""
        session_data["timestamp"] = datetime.utcnow()
        result = self.sessions.insert_one(session_data)
        return str(result.inserted_id)

    def get_session(self, session_id: str) -> dict:
        """Retrieve a session by ID for audit replay."""
        doc = self.sessions.find_one({"_id": ObjectId(session_id)})
        if doc:
            doc["_id"] = str(doc["_id"])  # Serialise ObjectId for JSON output
        return doc

    def search_policies(self, query: str) -> list:
        """Keyword search over policies collection (text index)."""
        results = list(
            self.policies_col.find(
                {"$text": {"$search": query}},
                {"_id": 0}
            ).limit(5)
        )
        return results

    def seed_policies(self, policies: list):
        """Seed policies into MongoDB (idempotent — skips if already present)."""
        if self.policies_col.count_documents({}) == 0:
            self.policies_col.insert_many(policies)
            print(f"[MongoDB] Seeded {len(policies)} policies.")
        else:
            print("[MongoDB] Policies already seeded — skipping.")
