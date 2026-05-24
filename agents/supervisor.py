from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from memory.mongo_utils import MongoUtils

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class ShadowRunSession(BaseModel):
    """Core IP artifact: versioned, structured compliance session record."""
    claim_id: str
    input_claim: dict
    retrieved_policies: List[dict]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    risk_score: float = Field(ge=0, le=100)
    triggered_policies: List[str]
    recommendation: Literal["APPROVE", "REJECT", "REMEDIATE"]
    rationale: str
    remediation_suggestion: Optional[str] = None
    # Extended fields for patent & replayability
    session_id: Optional[str] = None
    policy_version: Optional[str] = "v1.0"
    risk_factors: Optional[List[str]] = None


class SupervisorAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.mongo = MongoUtils()

    def search_policies(self, query: str) -> List[dict]:
        """Tool: retrieve relevant policies from MongoDB by keyword."""
        return self.mongo.search_policies(query)

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}. Raw output (first 500 chars): {text[:500]}...")
            raise ValueError("Gemini did not return valid JSON. Check prompt or model output.")

    def run_shadow_simulation(self, claim: dict, policies: List[dict]) -> ShadowRunSession:
        prompt = f"""
You are a compliance supervisor agent for RegOps Shield.
Perform a pre-execution shadow-run simulation for this insurance claim.

Claim:
{json.dumps(claim, indent=2)}

Retrieved Policies:
{json.dumps(policies, indent=2)}

Strict Guardrails:
- If any required claim field is missing or unclear → risk_level="HIGH", recommendation="REMEDIATE"
- If claim_amount > 100000 AND any policy is triggered → do NOT return "APPROVE"
- Always return valid JSON only. No extra text, no markdown fences.

Respond with exact JSON matching this schema:
{{
  "claim_id": string,
  "input_claim": object,
  "retrieved_policies": array,
  "risk_level": "LOW"|"MEDIUM"|"HIGH",
  "risk_score": number (0-100),
  "triggered_policies": array of strings,
  "recommendation": "APPROVE"|"REJECT"|"REMEDIATE",
  "rationale": string,
  "remediation_suggestion": string or null,
  "risk_factors": array of strings
}}
"""
        response = self.model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )
        data = self._parse_json(response.text)
        return ShadowRunSession(**data)
