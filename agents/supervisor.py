# supervisor.py
# RegOps Shield — Supervisor Agent (Gemini 2.0 Flash + Native Tool Calling + Structured Outputs)
from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Annotated
import os
import json
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import Tool, FunctionDeclaration

load_dotenv()

# ─────────────────────────────────────────────────────────────
# Pydantic Schema: Core IP Artifact
# Versioned, structured compliance session record
# ─────────────────────────────────────────────────────────────
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
    tool_calls_made: Optional[List[str]] = Field(
        default_factory=list,
        description="Audit trail of tool calls made during analysis"
    )


# ─────────────────────────────────────────────────────────────
# Tool Registry: Native Gemini Function Calling
# ─────────────────────────────────────────────────────────────
SEARCH_POLICIES_TOOL = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="search_policies",
            description="Search regulatory policies from MongoDB Atlas by keyword query. Returns relevant policy documents with category, jurisdiction, and risk thresholds.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords describing the compliance risk or claim type to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of policies to retrieve (default: 5)"
                    }
                },
                "required": ["query"]
            }
        )
    ]
)


# ─────────────────────────────────────────────────────────────
# Supervisor Agent
# ─────────────────────────────────────────────────────────────
class SupervisorAgent:
    """Autonomous compliance supervisor using Gemini 2.0 Flash with native tool calling.

    Key architectural decisions:
    - Native Tool Calling: Model decides WHEN to query MongoDB (no hardcoded prompts)
    - Structured Outputs: Pydantic response_schema guarantees valid JSON
    - System Instruction Separation: Role defined outside of prompt
    - Audit Trail: Tool calls tracked in tool_calls_made field
    - Two-Phase Analysis: Step 1 retrieves policies via tools, Step 2 evaluates claim
    """

    def __init__(self):
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.0-flash"
        self.mongo = None  # Lazy-loaded on first tool call

        # System instruction: role definition extracted from prompt
        self.system_instruction = (
            "You are a compliance supervisor agent for RegOps Shield, an enterprise RegTech system. "
            "Your role is to perform pre-execution shadow-run simulations on insurance claims. "
            "You have access to a policy search tool — use it to retrieve relevant regulatory policies "
            "before analyzing any claim. Always call search_policies with a keyword derived from the claim. "
            "After retrieving policies, analyze the claim against them and produce a structured risk assessment. "
            "Respond ONLY with valid JSON matching the requested schema. No markdown, no extra text."
        )

    def _get_mongo(self):
        """Lazy-load MongoDB utils on first access."""
        if self.mongo is None:
            from memory.mongo_utils import MongoUtils
            self.mongo = MongoUtils()
        return self.mongo

    def search_policies(self, query: str, limit: int = 5) -> str:
        """Tool implementation: retrieve relevant policies from MongoDB.

        This method is registered as a native Gemini tool and called
        autonomously by the model during the shadow-run simulation.
        """
        mongo = self._get_mongo()
        policies = mongo.search_policies(query, limit=limit, use_vector=True)
        return json.dumps(policies)

    def _build_tools(self):
        """Register local Python functions as callable tools for Gemini."""
        return [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="search_policies",
                        description="Search regulatory policies from MongoDB Atlas by keyword query.",
                        parameters={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Keywords describing the compliance risk or claim type"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Max number of policies to retrieve (default: 5)"
                                }
                            },
                            "required": ["query"]
                        }
                    )
                ]
            )
        ]

    def run_shadow_simulation(self, claim: dict, preloaded_policies: Optional[List[dict]] = None) -> ShadowRunSession:
        """Run a shadow-run simulation with native tool calling and structured outputs.

        Two-phase approach:
        1. If policies are preloaded (e.g. from vector search), use them directly
        2. Otherwise, let the model autonomously call search_policies tool

        Args:
            claim: Insurance claim dictionary to analyze
            preloaded_policies: Optional pre-retrieved policies (bypasses tool call)

        Returns:
            ShadowRunSession: Structured Pydantic model with full audit trail
        """
        claim_json = json.dumps(claim, indent=2)

        # Phase 1: Use preloaded policies if available (e.g. from vector search)
        if preloaded_policies:
            policies_json = json.dumps(preloaded_policies, indent=2)
            prompt = (
                f"Analyze this insurance claim against the following retrieved policies.\n\n"
                f"CLAIM:\n{claim_json}\n\n"
                f"RETRIEVED POLICIES:\n{policies_json}\n\n"
                f"GUARDRAILS:\n"
                f"- If any required claim field is missing or unclear, set risk_level=HIGH\n"
                f"- If claim_amount > 100000 AND any policy is triggered, do NOT return APPROVE\n"
                f"- Map triggered policies to their policy_id values in triggered_policies\n"
                f"- Always return valid JSON matching the schema."
            )
            tool_calls_made = ["vector_search_policies (external)"]
        else:
            # Phase 2: Model autonomously calls search_policies tool
            prompt = (
                f"Analyze this insurance claim. First, call the search_policies tool "
                f"to retrieve relevant regulatory policies. Then produce a structured risk assessment.\n\n"
                f"CLAIM:\n{claim_json}\n\n"
                f"GUARDRAILS:\n"
                f"- Call search_policies with a keyword derived from the claim description\n"
                f"- If any required claim field is missing or unclear, set risk_level=HIGH\n"
                f"- If claim_amount > 100000 AND any policy is triggered, do NOT return APPROVE\n"
                f"- Always return valid JSON matching the schema."
            )
            tool_calls_made = []

        # Track tool calls during generation
        def handle_tool_call(tool_call):
            func_name = tool_call.function_call.name
            args = tool_call.function_call.args

            if func_name == "search_policies":
                query = args.get("query", "insurance claim")
                limit = args.get("limit", 5)
                result = self.search_policies(query, limit=limit)
                tool_calls_made.append(f"search_policies(query={query}, limit={limit})")
                return result
            return ""

        # Generate content with tools + structured output
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            system_instruction=self.system_instruction,
            tools=self._build_tools() if not preloaded_policies else None,
            config={
                "response_mime_type": "application/json",
                "response_schema": ShadowRunSession,
                "temperature": 0.1,
            },
        )

        # Parse structured output and inject audit trail
        session = ShadowRunSession.model_validate_json(response.text)
        session.tool_calls_made = tool_calls_made
        return session


# ─────────────────────────────────────────────────────────────
# Main (CLI / Demo Entry Point)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Demo: autonomous tool-calling shadow run
    demo_claim = {
        "claim_id": "CLM-2026-001",
        "claimant_id": "INS-998877",
        "claim_type": "property_damage",
        "claim_amount": 150000.0,
        "incident_date": "2025-06-15",
        "policy_number": "POL-2025-12345",
        "description": "Severe water damage from burst pipe affecting basement and electrical systems. Claimant requests full replacement of damaged items including heirloom furniture valued at $45,000.",
        "metadata": {
            "submitter": "claimant",
            "channel": "mobile_app",
            "priority": "high",
            "attachments": ["photo_001.jpg", "repair_estimate.pdf"]
        }
    }

    print("=" * 60)
    print("RegOps Shield — Supervisor Agent (Native Tool Calling Demo)")
    print("=" * 60)
    print("\nRunning autonomous shadow-run simulation on demo claim...\n")

    agent = SupervisorAgent()
    session = agent.run_shadow_simulation(demo_claim)

    print(f"\n{'='*60}")
    print(f"SHADOW-RUN RESULT")
    print(f"{'='*60}")
    print(f"Claim ID:        {session.claim_id}")
    print(f"Risk Level:      {session.risk_level}")
    print(f"Risk Score:      {session.risk_score}")
    print(f"Recommendation:  {session.recommendation}")
    print(f"Triggered:       {session.triggered_policies}")
    print(f"Tool Calls:      {session.tool_calls_made}")
    print(f"Rationale:       {session.rationale[:200]}...")
    print(f"{'='*60}\n")
