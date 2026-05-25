# mongo_utils.py
# RegOps Shield — MongoDB Memory Layer with Atlas Vector Search

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from typing import List, Dict, Any, Optional

load_dotenv()

class MongoUtils:
    """MongoDB data access layer with keyword + vector search support.

    Vector Search (Atlas):
    - Uses MongoDB Atlas Vector Search (v1+)
    - Embeddings generated via Google text-embedding-004
    - Search index name: 'policies_vector_index'
    """

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client["regops_shield"]
        self.sessions = self.db["shadow_sessions"]
        self.policies_col = self.db["policies"]
        # Ensure text index on policies for keyword retrieval
        self.policies_col.create_index([("text", "text")], default_language="english")
        self.embedding_key = os.getenv("GEMINI_API_KEY")

    def save_session(self, session_data: dict) -> str:
        """Persist a ShadowRunSession document and return its MongoDB ID."""
        session_data["timestamp"] = datetime.utcnow()
        result = self.sessions.insert_one(session_data)
        return str(result.inserted_id)

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a session by ID for audit replay."""
        doc = self.sessions.find_one({"_id": ObjectId(session_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def search_policies(self, query: str, limit: int = 5, use_vector: bool = False) -> List[dict]:
        """Search policies by keyword or vector similarity.

        Args:
            query: Search text (keyword or for embedding generation)
            limit: Max results to return
            use_vector: If True, use Atlas Vector Search; else use text index

        Returns:
            List of matching policy documents (without _id)
        """
        if use_vector and self.embedding_key:
            return self._vector_search_policies(query, limit)
        # Fallback: keyword text search
        results = list(
            self.policies_col.find(
                {"$text": {"$search": query}},
                {"_id": 0}
            ).limit(limit)
        )
        return results

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Google text-embedding-004."""
        from google.genai import Client
        client = Client(api_key=self.embedding_key)
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        return response.embeddings[0].values

    def _vector_search_policies(self, query: str, limit: int = 5) -> List[dict]:
        """Atlas Vector Search: semantic policy retrieval.

        Requires a 'policies_vector_index' search index on the Atlas cluster
        with path 'embedding' and dimensions 768.
        """
        query_embedding = self._generate_embedding(query)
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "policies_vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "policy_id": 1,
                    "category": 1,
                    "jurisdiction": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        results = list(self.policies_col.aggregate(pipeline))
        return results

    def store_policy_with_embedding(self, policy: dict) -> None:
        """Store a policy document along with its vector embedding."""
        if not self.embedding_key:
            self.policies_col.insert_one(policy)
            return
        embedding = self._generate_embedding(policy.get("text", ""))
        policy["embedding"] = embedding
        self.policies_col.insert_one(policy)

    def seed_policies(self, policies: list) -> None:
        """Seed policies (optionally with embeddings) into MongoDB."""
        if self.policies_col.count_documents({}) == 0:
            for p in policies:
                self.store_policy_with_embedding(p)
            print(f"[MongoDB] Seeded {len(policies)} policies with embeddings.")
        else:
            print("[MongoDB] Policies already seeded — skipping.")
