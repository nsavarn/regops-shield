# mongo_utils.py
# RegOps Shield — MongoDB Memory Layer with Atlas Vector Search
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from typing import List, Dict, Any, Optional

load_dotenv()

logger = logging.getLogger(__name__)


class MongoUtils:
    """MongoDB data access layer with keyword + vector search support.

    Vector Search (Atlas):
    - Uses MongoDB Atlas Vector Search (v1+)
    - Embeddings generated via Google text-embedding-004
    - Search index name: 'policies_vector_index'
    - Dimensions: 768 ( embedding-004 default)

    Collections:
    - policies: Regulatory policy documents with optional embeddings
    - shadow_sessions: Audit trail of compliance shadow-run sessions
    """

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("ATLAS_DATABASE", "regops_shield")]
        self.sessions = self.db["shadow_sessions"]
        self.policies_col = self.db["policies"]

        # Ensure text index for keyword search
        self.policies_col.create_index(
            [("text", "text")],
            default_language="english"
        )

        self.embedding_key = os.getenv("GEMINI_API_KEY")
        self.embedding_model = os.getenv("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")

        logger.info("MongoDB connection initialized")

    # ─────────────────────────────────────────────────────────────
    # Session Management (Audit Trail)
    # ─────────────────────────────────────────────────────────────
    def save_session(self, session_data: dict) -> str:
        """Persist a ShadowRunSession document and return its MongoDB ID."""
        session_data["timestamp"] = datetime.utcnow()
        result = self.sessions.insert_one(session_data)
        logger.info(f"Session saved: {result.inserted_id}")
        return str(result.inserted_id)

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a session by ID for audit replay."""
        doc = self.sessions.find_one({"_id": ObjectId(session_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def update_session(self, session_id: str, updates: dict) -> bool:
        """Update a session document with new fields (e.g., remediation suggestions)."""
        result = self.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def list_sessions(self, limit: int = 10) -> List[dict]:
        """List recent shadow-run sessions for audit dashboard."""
        cursor = self.sessions.find(
            {},
            {
                "_id": 1,
                "claim_id": 1,
                "risk_level": 1,
                "risk_score": 1,
                "recommendation": 1,
                "timestamp": 1
            }
        ).sort("timestamp", -1).limit(limit)

        sessions = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            if isinstance(doc.get("timestamp"), datetime):
                doc["timestamp"] = doc["timestamp"].isoformat() + "Z"
            sessions.append(doc)
        return sessions

    # ─────────────────────────────────────────────────────────────
    # Policy Search (Keyword + Vector)
    # ─────────────────────────────────────────────────────────────
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
            return self.vector_search_policies(query, limit)

        # Fallback: keyword text search
        results = list(
            self.policies_col.find(
                {"$text": {"$search": query}},
                {"_id": 0}
            ).limit(limit)
        )
        return results

    def vector_search_policies(self, query: str, limit: int = 5) -> List[dict]:
        """Atlas Vector Search: semantic policy retrieval.

        Requires a 'policies_vector_index' search index on the Atlas cluster
        with path 'embedding' and dimensions 768.

        This is the public method called by app.py and supervisor.py.
        Falls back to keyword search if vector search fails (e.g., index not created).
        """
        try:
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
            logger.info(f"Vector search returned {len(results)} results for query: {query[:50]}")
            return results

        except Exception as e:
            logger.warning(f"Vector search failed, falling back to keyword: {e}")
            return self.search_policies(query, limit=limit, use_vector=False)

    # ─────────────────────────────────────────────────────────────
    # Embedding Generation (Google text-embedding-004)
    # ─────────────────────────────────────────────────────────────
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Google text-embedding-004."""
        from google.genai import Client

        client = Client(api_key=self.embedding_key)
        response = client.models.embed_content(
            model=self.embedding_model,
            contents=text,
        )
        return response.embeddings[0].values

    # ─────────────────────────────────────────────────────────────
    # Policy Storage (with Embeddings)
    # ─────────────────────────────────────────────────────────────
    def store_policy_with_embedding(self, policy: dict) -> None:
        """Store a policy document along with its vector embedding."""
        if not self.embedding_key:
            self.policies_col.insert_one(policy)
            return

        embedding = self._generate_embedding(policy.get("text", ""))
        policy["embedding"] = embedding
        self.policies_col.insert_one(policy)
        logger.info(f"Stored policy with embedding: {policy.get('policy_id', 'unknown')}")

    def seed_policies(self, policies: list) -> None:
        """Seed policies (optionally with embeddings) into MongoDB."""
        if self.policies_col.count_documents({}) == 0:
            for p in policies:
                self.store_policy_with_embedding(p)
            logger.info(f"Seeded {len(policies)} policies with embeddings.")
        else:
            logger.info("Policies already seeded — skipping.")

    # ─────────────────────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────────────────────
    def health_check(self) -> bool:
        """Check if MongoDB connection is alive."""
        try:
            self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False
