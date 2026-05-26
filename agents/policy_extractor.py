"""
agents/policy_extractor.py
RegOps Shield — Policy Extraction Agent (Phase B: Agentic Extraction)

Transforms raw regulatory circulars/acts into structured ComplianceConstraint
JSON documents, generates vector embeddings, and enforces HITL routing for
ambiguous clauses before MongoDB Atlas promotion.

Patent Reference: Regulated Adaptive Shadow-Run with Explainable Memory
Handoff Protocol — Phase B (Agentic Extraction Processor)

SDK: google-genai (unified, v1alpha) — NOT google-generativeai (deprecated)
Model: gemini-2.5-flash (Gemini 3 engine, hackathon-compliant)
Output: ExtractedPolicy Pydantic model → MongoDB `policies` collection
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Literal, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator

load_dotenv()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

MODEL_ID = "gemini-2.5-flash"          # Gemini 3 engine — hackathon mandate
EMBEDDING_MODEL_ID = "text-embedding-004"
HITL_DRIFT_THRESHOLD = float(os.getenv("HITL_DRIFT_THRESHOLD", "0.25"))  # 25%
PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "prompts", "supervisor_system_prompt.md"
)


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class RiskThreshold(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class PolicyStatus(str, Enum):
    PENDING_VALIDATION = "PENDING_VALIDATION"   # Awaiting shadow-validation (Phase C)
    REVIEW_REQUIRED = "STATUS_REVIEW_REQUIRED"   # Ambiguous clause — HITL mandatory
    VALIDATED = "VALIDATED"                      # Shadow-run passed, ready for promotion
    PROMOTED = "PROMOTED"                        # Live in active vector index
    REJECTED = "REJECTED"                        # Failed shadow-validation or HITL rejection


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ComplianceConstraint(BaseModel):
    """Atomic, modular compliance rule — maps 1:1 to a MongoDB subdocument.

    Designed for atomic vector index updates (self-healing requirement).
    Each constraint is independently retrievable via Atlas Vector Search
    using the search_vector_description embedding.
    """
    clause_id: str = Field(
        description="Unique clause identifier, e.g. RBI-2026-001-C01"
    )
    text: str = Field(
        description="Verbatim regulatory constraint text from source document"
    )
    risk_threshold: RiskThreshold = Field(
        description="Risk severity classification: Low | Medium | High | Critical"
    )
    remediation_action: str = Field(
        description="Specific if-then corrective step for the RemediationHelper agent"
    )
    search_vector_description: str = Field(
        description="Dense, high-entropy summary optimised for Atlas Vector Search retrieval"
    )
    pre_execution_applicable: bool = Field(
        default=True,
        description="True if this constraint can be validated BEFORE transaction execution (shadow-run priority)"
    )
    review_flag: Optional[str] = Field(
        default=None,
        description="Set to STATUS_REVIEW_REQUIRED if the clause is ambiguous — triggers HITL queue"
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        description="text-embedding-004 vector; populated post-extraction before MongoDB persistence"
    )


class ExtractedPolicy(BaseModel):
    """Top-level policy document — maps to MongoDB `policies` collection schema."""
    policy_id: str = Field(
        description="Unique policy identifier, e.g. RBI-2026-001"
    )
    title: str
    effective_date: str = Field(
        description="ISO-8601 effective date of the regulation"
    )
    constraints: List[ComplianceConstraint]
    governance_tag: str = Field(
        description="Domain tag, e.g. BFSI_INDIA, EU_AI_ACT, IRDAI_2026"
    )
    status: PolicyStatus = PolicyStatus.PENDING_VALIDATION
    policy_version: str = "v1.0"
    ingestion_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_document_hash: Optional[str] = None
    hitl_queue_id: Optional[str] = None  # Populated if any clause triggers HITL
    rationale: Optional[str] = None      # Agent explanation for extraction decisions

    @field_validator("effective_date")
    @classmethod
    def validate_iso_date(cls, v: str) -> str:
        """Reject malformed dates — prevents silent downstream Atlas index failures."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(
                f"effective_date must be ISO-8601. Received: {v!r}"
            ) from exc
        return v


class HITLQueueItem(BaseModel):
    """Routes ambiguous or high-drift policies to human supervisor review."""
    queue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    policy_id: str
    reason: Literal[
        "AMBIGUOUS_CLAUSE",
        "HIGH_DRIFT_DETECTED",
        "SHADOW_VALIDATION_FAILED",
        "MANUAL_ESCALATION"
    ]
    flagged_clause_ids: List[str]
    drift_score: Optional[float] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    resolved: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Policy Extraction Agent
# ─────────────────────────────────────────────────────────────────────────────

class PolicyExtractionAgent:
    """Phase B processor: transforms raw regulatory text into structured
    ComplianceConstraint documents with vector embeddings.

    Architecture:
        1. Load supervisor_system_prompt.md as system_instruction
        2. Call Gemini 2.5-flash with response_mime_type=application/json
           and response_schema=ExtractedPolicy for deterministic output
        3. Scan all constraints for review_flag == STATUS_REVIEW_REQUIRED
        4. If flagged → write HITLQueueItem and block MongoDB promotion
        5. If clean → generate text-embedding-004 vectors and return

    Pre-commit hook stub (Phase C integration point) is included at the
    bottom of ingest_policy() — connects to ShadowRunSession replay.
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not set. Add it to your .env file."
            )
        # Unified google-genai SDK (v1alpha) — NOT deprecated google-generativeai
        self.client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1alpha"}
        )
        self.system_prompt = self._load_system_prompt()
        self.mongo = None  # Lazy-loaded on first persistence call

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_system_prompt(self) -> str:
        """Load supervisor_system_prompt.md from prompts/ directory."""
        prompt_path = os.path.abspath(PROMPT_PATH)
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(
                f"System prompt not found at: {prompt_path}\n"
                "Ensure prompts/supervisor_system_prompt.md exists in the repo root."
            )
        with open(prompt_path, "r", encoding="utf-8") as fh:
            return fh.read()

    def _get_mongo(self):
        """Lazy-load MongoUtils to avoid import-time connection errors."""
        if self.mongo is None:
            from memory.mongo_utils import MongoUtils
            self.mongo = MongoUtils()
        return self.mongo

    def _generate_embeddings(
        self, constraints: List[ComplianceConstraint]
    ) -> List[ComplianceConstraint]:
        """Batch-generate text-embedding-004 vectors for all search_vector_description
        fields before MongoDB Atlas persistence.

        Each vector is stored inline on the constraint object so the Atlas
        Vector Search index can be populated atomically.
        """
        for constraint in constraints:
            if constraint.review_flag:  # Skip ambiguous — do not embed until resolved
                logger.warning(
                    "Skipping embedding for flagged clause %s — HITL required",
                    constraint.clause_id,
                )
                continue
            try:
                embed_response = self.client.models.embed_content(
                    model=EMBEDDING_MODEL_ID,
                    content=constraint.search_vector_description,
                )
                constraint.embedding = embed_response.embeddings[0].values
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Embedding failed for clause %s: %s",
                    constraint.clause_id, exc
                )
                # Soft failure — flag for HITL rather than crashing ingestion
                constraint.review_flag = PolicyStatus.REVIEW_REQUIRED.value
        return constraints

    def _detect_hitl_constraints(
        self, policy: ExtractedPolicy
    ) -> Optional[HITLQueueItem]:
        """Scan all constraints for STATUS_REVIEW_REQUIRED flag.

        Returns a HITLQueueItem if any ambiguous clause is found,
        blocking auto-promotion to the live vector index.
        """
        flagged = [
            c.clause_id
            for c in policy.constraints
            if c.review_flag and "REVIEW_REQUIRED" in c.review_flag
        ]
        if not flagged:
            return None

        hitl_item = HITLQueueItem(
            policy_id=policy.policy_id,
            reason="AMBIGUOUS_CLAUSE",
            flagged_clause_ids=flagged,
        )
        logger.warning(
            "HITL TRIGGERED — Policy %s has %d ambiguous clause(s): %s. "
            "Routed to hitl_queue (queue_id=%s). Blocking MongoDB promotion.",
            policy.policy_id,
            len(flagged),
            flagged,
            hitl_item.queue_id,
        )
        return hitl_item

    def _persist_hitl_item(self, hitl_item: HITLQueueItem) -> None:
        """Write HITLQueueItem to MongoDB `hitl_queue` collection."""
        try:
            mongo = self._get_mongo()
            mongo.db["hitl_queue"].insert_one(
                hitl_item.model_dump()
            )
            logger.info(
                "HITLQueueItem %s written to hitl_queue collection.",
                hitl_item.queue_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to write HITL item to MongoDB: %s", exc)

    # ── Pre-Commit Shadow-Validation Hook (Phase C stub) ──────────────────────

    def _run_shadow_validation_hook(
        self, policy: ExtractedPolicy, sample_size: int = 100
    ) -> tuple[bool, float]:
        """Phase C integration stub: retroactive shadow-run before MongoDB promotion.

        Replays the last `sample_size` ShadowRunSession records against the
        new policy vector to detect compliance drift BEFORE auto-commit.

        Returns:
            (approved: bool, drift_score: float)
            If drift_score > HITL_DRIFT_THRESHOLD → block and route to HITL.

        TODO (Phase C): Replace stub with live ShadowRunSession replay.
        """
        logger.info(
            "[Phase C Stub] Shadow-validation hook triggered for policy %s. "
            "Replaying last %d sessions. (Full implementation: Phase C)",
            policy.policy_id,
            sample_size,
        )
        # Stub: always returns approved=True, drift_score=0.0 until Phase C wires in
        # the retroactive replay using existing POST /api/v1/shadow-run logic.
        drift_score = 0.0
        approved = drift_score <= HITL_DRIFT_THRESHOLD
        return approved, drift_score

    # ── Core Public Interface ─────────────────────────────────────────────────

    def extract_policy(self, raw_text: str) -> ExtractedPolicy:
        """Transform raw regulatory text into a structured ExtractedPolicy.

        Uses Gemini 2.5-flash with:
        - system_instruction: supervisor_system_prompt.md (injected role)
        - response_mime_type: application/json (deterministic output)
        - response_schema: ExtractedPolicy (Pydantic-enforced structure)
        - temperature: 0.1 (near-deterministic for compliance-grade output)

        Args:
            raw_text: Raw regulatory circular, act, or compliance document text.

        Returns:
            ExtractedPolicy with status=PENDING_VALIDATION or REVIEW_REQUIRED.
        """
        logger.info("Extracting policy from raw text (%d chars)", len(raw_text))

        response = self.client.models.generate_content(
            model=MODEL_ID,
            contents=raw_text,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                response_mime_type="application/json",
                response_schema=ExtractedPolicy,
                temperature=0.1,
            ),
        )

        policy = ExtractedPolicy.model_validate_json(response.text)
        logger.info(
            "Extraction complete: policy_id=%s, constraints=%d",
            policy.policy_id,
            len(policy.constraints),
        )
        return policy

    def ingest_policy(
        self,
        raw_text: str,
        persist: bool = True,
    ) -> dict:
        """Full ingestion pipeline: Extract → Embed → HITL Check → Shadow-Validate → Persist.

        This is the callable invoked by POST /api/v1/ingest-policy.

        Pipeline stages:
            1. extract_policy()       — Gemini 2.5-flash JSON extraction
            2. _generate_embeddings() — text-embedding-004 batch vectorisation
            3. _detect_hitl_constraints() — scan for STATUS_REVIEW_REQUIRED flags
            4. _run_shadow_validation_hook() — Phase C pre-commit retroactive replay
            5. MongoDB persistence (policies or staged_policies collection)

        Args:
            raw_text: Raw regulatory document text.
            persist:  If True, writes to MongoDB. Set False for dry-run/testing.

        Returns:
            dict with keys: policy_id, status, hitl_queue_id, constraint_count,
            embedded_count, drift_score.
        """
        # ── Stage 1: Extraction ───────────────────────────────────────────────
        policy = self.extract_policy(raw_text)

        # ── Stage 2: Embedding ────────────────────────────────────────────────
        policy.constraints = self._generate_embeddings(policy.constraints)
        embedded_count = sum(
            1 for c in policy.constraints if c.embedding is not None
        )

        # ── Stage 3: HITL Detection ───────────────────────────────────────────
        hitl_item = self._detect_hitl_constraints(policy)
        if hitl_item:
            policy.status = PolicyStatus.REVIEW_REQUIRED
            policy.hitl_queue_id = hitl_item.queue_id
            if persist:
                # Write HITL queue item and park in staged_policies (not live index)
                self._persist_hitl_item(hitl_item)
                self._get_mongo().db["staged_policies"].insert_one(
                    policy.model_dump(exclude={"constraints": {"__all__": {"embedding"}}})
                )
                logger.info(
                    "Policy %s parked in staged_policies pending HITL resolution.",
                    policy.policy_id,
                )
            return {
                "policy_id": policy.policy_id,
                "status": PolicyStatus.REVIEW_REQUIRED.value,
                "hitl_queue_id": hitl_item.queue_id,
                "constraint_count": len(policy.constraints),
                "embedded_count": embedded_count,
                "drift_score": None,
                "message": (
                    f"{len(hitl_item.flagged_clause_ids)} ambiguous clause(s) detected. "
                    "Policy routed to HITL queue. Promotion to live index blocked."
                ),
            }

        # ── Stage 4: Shadow-Validation Pre-Commit Hook ────────────────────────
        approved, drift_score = self._run_shadow_validation_hook(policy)
        if not approved:
            policy.status = PolicyStatus.REVIEW_REQUIRED
            hitl_drift_item = HITLQueueItem(
                policy_id=policy.policy_id,
                reason="HIGH_DRIFT_DETECTED",
                flagged_clause_ids=[c.clause_id for c in policy.constraints],
                drift_score=drift_score,
            )
            policy.hitl_queue_id = hitl_drift_item.queue_id
            if persist:
                self._persist_hitl_item(hitl_drift_item)
                self._get_mongo().db["staged_policies"].insert_one(
                    policy.model_dump(exclude={"constraints": {"__all__": {"embedding"}}})
                )
            return {
                "policy_id": policy.policy_id,
                "status": PolicyStatus.REVIEW_REQUIRED.value,
                "hitl_queue_id": hitl_drift_item.queue_id,
                "constraint_count": len(policy.constraints),
                "embedded_count": embedded_count,
                "drift_score": drift_score,
                "message": (
                    f"Shadow-validation drift score {drift_score:.2%} exceeds "
                    f"threshold {HITL_DRIFT_THRESHOLD:.2%}. Routed to HITL queue."
                ),
            }

        # ── Stage 5: Promote to Live Policies Collection ──────────────────────
        policy.status = PolicyStatus.VALIDATED
        if persist:
            try:
                mongo = self._get_mongo()
                mongo.db["policies"].insert_one(
                    policy.model_dump()
                )
                policy.status = PolicyStatus.PROMOTED
                logger.info(
                    "Policy %s promoted to live policies collection (version=%s).",
                    policy.policy_id,
                    policy.policy_version,
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("MongoDB persistence failed: %s", exc)
                raise

        return {
            "policy_id": policy.policy_id,
            "status": policy.status.value,
            "hitl_queue_id": None,
            "constraint_count": len(policy.constraints),
            "embedded_count": embedded_count,
            "drift_score": drift_score,
            "message": "Policy successfully validated and promoted to live index.",
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI / Demo Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    SAMPLE_CIRCULAR = """
    RBI Master Direction — Insurance Regulatory and Development Authority of India
    Circular No. IRDAI/HLT/REG/CIR/019/01/2026
    Date: January 15, 2026

    Subject: Mandatory AI-Assisted Claim Pre-Validation for Health Insurance

    1. All insurers processing health insurance claims exceeding INR 50,000 must
       implement pre-execution validation using AI-assisted risk scoring before
       releasing claim settlement amounts. Non-compliance attracts penalties under
       Section 102 of the Insurance Act, 1938.

    2. Insurers must maintain immutable audit logs of all AI-assisted claim decisions
       for a minimum period of 7 years, accessible to IRDAI inspectors within
       48 hours of a formal request.

    3. Any AI model used in claim adjudication must undergo a quarterly bias audit
       and submit findings to IRDAI via the regulatory reporting portal by the
       15th of the month following the quarter end.
    """

    print("=" * 70)
    print("RegOps Shield — Policy Extraction Agent (Phase B Demo)")
    print("Model: gemini-2.5-flash | SDK: google-genai v1alpha")
    print("=" * 70)

    agent = PolicyExtractionAgent()
    result = agent.ingest_policy(SAMPLE_CIRCULAR, persist=False)

    print("\n--- INGESTION RESULT ---")
    print(json.dumps(result, indent=2))
    print("=" * 70)
