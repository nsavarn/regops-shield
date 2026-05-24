import json
import sys
from agents.supervisor import SupervisorAgent
from memory.mongo_utils import MongoUtils
from agents.remediation import RemediationHelper


def load_data():
    with open("data/claims.json") as f:
        claims = json.load(f)
    with open("data/policies.json") as f:
        policies = json.load(f)
    return claims[0], policies


def main():
    claim, policies = load_data()
    print("=== RegOps Shield - Insurance Claim Triage Demo ===\n")
    print(f"Processing claim: {claim['claim_id']}")

    supervisor = SupervisorAgent()
    mongo = MongoUtils()
    remediation = RemediationHelper()

    # Shadow Run
    session = supervisor.run_shadow_simulation(claim, policies)
    print(f"\nRisk Level   : {session.risk_level} (Score: {session.risk_score})")
    print(f"Recommendation: {session.recommendation}")
    print(f"Rationale    : {session.rationale}")

    if session.remediation_suggestion:
        print(f"Initial Suggestion: {session.remediation_suggestion}")

    # Light Remediation
    final_remediation = remediation.get_remediation(session)
    print(f"Final Remediation : {final_remediation}")

    # Save to MongoDB & back-assign session_id
    session_dict = session.model_dump(exclude_none=True)
    session_id = mongo.save_session(session_dict)
    session.session_id = session_id
    print(f"\n✅ Audit memory saved with ID: {session_id}")
    print("\nShadow-run completed. Replayable audit memory persisted in MongoDB.")

    # Simple Replay Demo
    if len(sys.argv) > 1 and sys.argv[1] == "--replay":
        replay = mongo.get_session(session_id)
        print("\n--- REPLAY FROM MEMORY ---")
        print(json.dumps(replay, indent=2, default=str))


if __name__ == "__main__":
    main()
