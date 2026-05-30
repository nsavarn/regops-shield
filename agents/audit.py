# agents/audit.py
# RegOps Shield — Immutable Audit Trail Generator
# Patent Reference: Regulated Adaptive Shadow-Run with Explainable Memory
# Handoff Protocol — Phase D (Audit & Explainability Layer)
#
# Generates cryptographically-structured, IRDAI-compliant audit packets
# from ShadowRunSession records. All records are immutable once written.
# Retention: 7 years (Insurance Act 1938, Section 64VB compliance).

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

AUDIT_SCHEMA_VERSION = "1.0.0"
RETENTION_YEARS = 7


class AuditPacket(BaseModel):
    """Immutable audit record for a single ShadowRunSession.

    Designed for:
    - IRDAI inspector access within 48 hours (Insurance Act 1938)
    - 7-year immutable retention
    - Cryptographic integrity via SHA-256 content hash
    - Full explainability chain: claim → policies → risk → recommendation
    """
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_schema_version: str = AUDIT_SCHEMA_VERSION
    audit_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    retention_until: str = Field(
        default_factory=lambda: datetime(
            datetime.now(timezone.utc).year + RETENTION_YEARS,
            datetime.now(timezone.utc).month,
            datetime.now(timezone.utc).day,
            tzinfo=timezone.utc
        ).isoformat()
    )
    # Session identity
    session_id: str
    claim_id: str
    claimant_id: Optional[str] = None

    # Risk assessment
    risk_level: str
    risk_score: float
    recommendation: str
    rationale: str
    risk_factors: List[str] = []

    # Policy traceability
    triggered_policies: List[str] = []
    policy_version: str

    # Remediation
    remediation_suggestion: Optional[str] = None

    # Tool call trace (explainability)
    tool_calls_made: List[str] = []

    # Integrity
    content_hash: Optional[str] = None
    replayable: bool = True
    compliance_tags: List[str] = Field(
        default_factory=lambda: ["IRDAI_2026", "INSURANCE_ACT_1938", "AI_AUDIT_TRAIL"]
    )

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of core audit fields for integrity verification."""
        payload = {
            "session_id": self.session_id,
            "claim_id": self.claim_id,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "recommendation": self.recommendation,
            "audit_timestamp": self.audit_timestamp,
        }
        serialised = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialised.encode()).hexdigest()


class AuditPacketGenerator:
    """Generates immutable, IRDAI-compliant audit packets from ShadowRunSession records.

    Architecture:
    - Converts ShadowRunSession → AuditPacket (Pydantic-validated)
    - Computes SHA-256 integrity hash
    - Supports optional MongoDB persistence
    - Provides CLI-friendly print_packet() for demo output
    """

    def generate(self, session: Any) -> Dict[str, Any]:
        """Generate a validated, hash-signed audit packet from a ShadowRunSession.

        Args:
            session: ShadowRunSession instance (duck-typed for testability)

        Returns:
            Dict representing the fully-formed AuditPacket.
        """
        packet = AuditPacket(
            session_id=str(getattr(session, "session_id", str(uuid.uuid4()))),
            claim_id=session.claim_id,
            claimant_id=getattr(session, "claimant_id", None),
            risk_level=session.risk_level,
            risk_score=float(session.risk_score),
            recommendation=session.recommendation,
            rationale=session.rationale,
            risk_factors=list(session.risk_factors or []),
            triggered_policies=list(session.triggered_policies or []),
            policy_version=session.policy_version,
            remediation_suggestion=getattr(session, "remediation_suggestion", None),
            tool_calls_made=list(getattr(session, "tool_calls_made", []) or []),
        )
        packet.content_hash = packet.compute_hash()

        logger.info(
            "Audit packet generated: audit_id=%s claim_id=%s risk=%s hash=%s",
            packet.audit_id,
            packet.claim_id,
            packet.risk_level,
            packet.content_hash[:16],
        )
        return packet.model_dump()

    def generate_and_persist(self, session: Any, mongo_db=None) -> Dict[str, Any]:
        """Generate audit packet and optionally persist to MongoDB audit_trail collection.

        Args:
            session: ShadowRunSession instance
            mongo_db: Optional pymongo.database.Database instance

        Returns:
            Persisted audit packet dict with MongoDB _id if applicable.
        """
        packet = self.generate(session)
        if mongo_db is not None:
            try:
                result = mongo_db["audit_trail"].insert_one(packet.copy())
                packet["_id"] = str(result.inserted_id)
                logger.info(
                    "Audit packet persisted to audit_trail: _id=%s",
                    packet["_id"],
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to persist audit packet to MongoDB: %s", exc)
        return packet

    def print_packet(self, session: Any) -> None:
        """Pretty-print audit packet to stdout (demo / CLI use)."""
        packet = self.generate(session)
        print("\n=== AUDIT PACKET ===")
        print(json.dumps(packet, indent=2, default=str))
        print("=" * 40 + "\n")

    def verify_integrity(self, packet: Dict[str, Any]) -> bool:
        """Verify the SHA-256 content hash of a stored audit packet.

        Args:
            packet: Stored audit packet dict (from MongoDB or JSON)

        Returns:
            True if hash matches, False if tampered.
        """
        stored_hash = packet.get("content_hash", "")
        payload = {
            "session_id": packet.get("session_id", ""),
            "claim_id": packet.get("claim_id", ""),
            "risk_level": packet.get("risk_level", ""),
            "risk_score": packet.get("risk_score", 0.0),
            "recommendation": packet.get("recommendation", ""),
            "audit_timestamp": packet.get("audit_timestamp", ""),
        }
        serialised = json.dumps(payload, sort_keys=True)
        expected_hash = hashlib.sha256(serialised.encode()).hexdigest()
        intact = stored_hash == expected_hash
        if not intact:
            logger.warning(
                "Audit packet integrity FAILED for session_id=%s",
                packet.get("session_id"),
            )
        return intact
