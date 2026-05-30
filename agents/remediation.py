# agents/remediation.py
# RegOps Shield — Remediation Helper Agent
# Patent Reference: Regulated Adaptive Shadow-Run with Explainable Memory
# Handoff Protocol — Phase E (Remediation Action Engine)
#
# Maps ShadowRunSession outcomes to specific, IRDAI-compliant corrective actions.
# Supports risk-tier escalation, SLA deadlines, and MongoDB persistence.

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RemediationAction(BaseModel):
    """Structured remediation instruction generated from a ShadowRunSession.

    Each action is:
    - Risk-tier specific (LOW / MEDIUM / HIGH)
    - SLA-deadline bound (Insurance Act 1938 compliance)
    - Traceable back to source session_id and claim_id
    """
    action_id: str
    session_id: str
    claim_id: str
    risk_level: str
    recommendation: str
    action_description: str
    sla_deadline: str  # ISO-8601
    escalation_required: bool = False
    escalation_tier: Optional[str] = None
    compliance_tags: List[str] = Field(
        default_factory=lambda: ["IRDAI_2026", "INSURANCE_ACT_1938"]
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class RemediationHelper:
    """Transforms ShadowRunSession outcomes into structured remediation actions.

    Architecture:
    - Risk-tiered REMEDIATION_MAP with SLA windows
    - APPROVE / REJECT / REVIEW fast-paths
    - Pydantic-validated RemediationAction output
    - Optional MongoDB persistence for audit trail
    """

    # SLA windows per risk tier (Insurance Act 1938 / IRDAI 2026 mandate)
    _SLA_HOURS: Dict[str, int] = {
        "LOW": 72,       # 3 business days
        "MEDIUM": 48,    # 48 hours
        "HIGH": 24,      # 24 hours — mandatory senior sign-off
        "CRITICAL": 4,   # Immediate escalation
    }

    REMEDIATION_MAP: Dict[str, Dict[str, Any]] = {
        "HIGH": {
            "action": "Require additional documentation + mandatory senior review before settlement",
            "escalation_required": True,
            "escalation_tier": "SENIOR_UNDERWRITER",
        },
        "MEDIUM": {
            "action": "Request supplementary evidence within 48 hours; flag for compliance review",
            "escalation_required": False,
            "escalation_tier": None,
        },
        "LOW": {
            "action": "Proceed with partial approval + attach monitoring flag for 90-day review window",
            "escalation_required": False,
            "escalation_tier": None,
        },
    }

    def get_remediation(self, session: Any) -> str:
        """Return the primary remediation action string for a ShadowRunSession.

        Fast-path for APPROVE / REJECT; risk-tier lookup for REVIEW.

        Args:
            session: ShadowRunSession instance (duck-typed)

        Returns:
            Human-readable remediation action string.
        """
        recommendation = getattr(session, "recommendation", "").upper()
        risk_level = getattr(session, "risk_level", "LOW").upper()

        if recommendation == "APPROVE":
            return "Full Approval Recommended — no further action required"
        elif recommendation == "REJECT":
            return (
                "Claim Rejection — provide written explanation to claimant within 15 days "
                "(IRDAI Grievance Redressal Guidelines 2024)"
            )
        else:
            tier = self.REMEDIATION_MAP.get(risk_level, self.REMEDIATION_MAP["HIGH"])
            return tier["action"]

    def build_action(self, session: Any) -> RemediationAction:
        """Build a fully-structured RemediationAction from a ShadowRunSession.

        Args:
            session: ShadowRunSession instance

        Returns:
            Validated RemediationAction with SLA deadline and escalation metadata.
        """
        import uuid
        risk_level = getattr(session, "risk_level", "LOW").upper()
        sla_hours = self._SLA_HOURS.get(risk_level, 72)
        deadline = (datetime.now(timezone.utc) + timedelta(hours=sla_hours)).isoformat()

        tier = self.REMEDIATION_MAP.get(risk_level, self.REMEDIATION_MAP["HIGH"])
        action_desc = self.get_remediation(session)

        action = RemediationAction(
            action_id=str(uuid.uuid4()),
            session_id=str(getattr(session, "session_id", "")),
            claim_id=session.claim_id,
            risk_level=risk_level,
            recommendation=getattr(session, "recommendation", "REVIEW"),
            action_description=action_desc,
            sla_deadline=deadline,
            escalation_required=tier.get("escalation_required", False),
            escalation_tier=tier.get("escalation_tier"),
        )
        logger.info(
            "Remediation action built: claim_id=%s risk=%s escalation=%s sla=%s",
            action.claim_id,
            action.risk_level,
            action.escalation_required,
            action.sla_deadline,
        )
        return action

    def build_and_persist(self, session: Any, mongo_db=None) -> Dict[str, Any]:
        """Build RemediationAction and optionally persist to MongoDB.

        Args:
            session: ShadowRunSession instance
            mongo_db: Optional pymongo.database.Database instance

        Returns:
            RemediationAction as dict, with optional MongoDB _id.
        """
        action = self.build_action(session)
        action_dict = action.model_dump()

        if mongo_db is not None:
            try:
                result = mongo_db["remediation_actions"].insert_one(action_dict.copy())
                action_dict["_id"] = str(result.inserted_id)
                logger.info(
                    "Remediation action persisted: _id=%s claim_id=%s",
                    action_dict["_id"],
                    action.claim_id,
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to persist remediation action: %s", exc)

        return action_dict
