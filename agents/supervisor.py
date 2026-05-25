# supervisors.py
# RegOps Shield — Supervisor Agent (Gemini 2.0 + Native Structured Outputs)

from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import os
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import Tool, FunctionDeclaration

load_dotenv()

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
    session_id: Optional[str] = None
    policy_version: Optional[str] = "v1.0"
    risk_factors: Optional[List[str]] = None
    evidence_summary: Optional[str] = None

class SupervisorAgent:
    def __init__(self):
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.0-flash"
        # System instruction: moved out of prompt for cleaner API usage
        self.system_instruction = """You are a compliance supervisor agent for RegOps Shield, an enterprise RegTech system.
Your role is to perform pre-execution shadow-run simulations on insurance claims.
Analyze claims against retrieved regulatory policies and produce structured risk assessments.
Respond ONLY with valid JSON matching the requested schema. No markdown, no explanations outside the JSON."""

    def search_policies(self, query: str, limit: int = 5) -> List[dict]:
        """Tool: retrieve relevant policies from MongoDB by keyword."""
        from memory.mongo_utils import MongoUtils
        mongo = MongoUtils()
        return mongo.search_policies(query, limit=limit)

    def run_shadow_simulation(self, claim: dict, policies: List[dict]) -> ShadowRunSession:
        """Run a shadow-run simulation with native structured output support."""
        claim_json = __import__("json").dumps(claim, indent=2)
        policies_json = __import__("json").dumps(policies, indent=2)

        prompt = f"""Analyze this insurance claim against the retrieved policies.

Claim:
{claim_json}

Retrieved Policies:
{policies_json}

Apply these guardrails:
- If any required claim field is missing or unclear, set risk_level="HIGH", recommendation="REMEDIATE"
- If claim_amount > 100000 AND any policy is triggered, do NOT return "APPROVE"
- Always return valid JSON."""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            system_instruction=self.system_instruction,
            config={
                "response_mime_type": "application/json",
                "response_schema": ShadowRunSession,
                "temperature": 0.1,
            },
        )
        return ShadowRunSession.model_validate_json(response.text)
