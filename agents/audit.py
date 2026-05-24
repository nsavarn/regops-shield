from agents.supervisor import ShadowRunSession
from datetime import datetime


class AuditPacketGenerator:
    """Generates human-readable audit packets from ShadowRunSession records."""

    def generate(self, session: ShadowRunSession) -> dict:
        return {
            "audit_timestamp": datetime.utcnow().isoformat() + "Z",
            "claim_id": session.claim_id,
            "session_id": session.session_id,
            "risk_level": session.risk_level,
            "risk_score": session.risk_score,
            "recommendation": session.recommendation,
            "triggered_policies": session.triggered_policies,
            "risk_factors": session.risk_factors or [],
            "rationale": session.rationale,
            "remediation_suggestion": session.remediation_suggestion,
            "policy_version": session.policy_version,
            "replayable": True,
        }

    def print_packet(self, session: ShadowRunSession):
        import json
        packet = self.generate(session)
        print("\n=== AUDIT PACKET ===")
        print(json.dumps(packet, indent=2))
        print("===================\n")
