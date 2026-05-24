from agents.supervisor import ShadowRunSession


class RemediationHelper:
    """Light remediation helper — pure Python mapping of risk/policies to actions."""

    REMEDIATION_MAP = {
        "HIGH": "Require additional documentation + senior review",
        "MEDIUM": "Request supplementary evidence within 48 hours",
        "LOW": "Proceed with partial approval + monitoring flag",
    }

    def get_remediation(self, session: ShadowRunSession) -> str:
        if session.recommendation == "APPROVE":
            return "Full Approval Recommended — no further action required"
        elif session.recommendation == "REJECT":
            return "Claim Rejection — explanation to be provided to claimant"
        else:
            return self.REMEDIATION_MAP.get(session.risk_level, "Human Escalation Required")
