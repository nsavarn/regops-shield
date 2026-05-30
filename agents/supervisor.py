# supervisor.py
# RegOps Shield — Supervisor Agent (Gemini 2.0 Flash + Native Tool Calling + Structured Outputs)
# Version: v1.0.0-GA

import os
import json
import logging
from typing import Literal, List, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import Tool, FunctionDeclaration, GenerateContentConfig

load_dotenv()
logger = logging.getLogger(__name__)

# Path to the system prompt file (shared with policy_extractor)
_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "supervisor_system_prompt.md")


def _load_system_prompt() -> str:
    """Load supervisor system instruction from prompts/supervisor_system_prompt.md."""
    path = os.path.abspath(_PROMPT_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"System prompt not found at: {path}\n"
            "Ensure prompts/supervisor_system_prompt.md exists in the repo root."
        )
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


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
        description="Audit trail of tool calls made during shadow-run analysis"
    )


# ─────────────────────────────────────────────────────────────
# Supervisor Agent
# ─────────────────────────────────────────────────────────────
class SupervisorAgent:
    """Autonomous compliance supervisor using Gemini 2.0 Flash with native tool calling.

    Key architectural decisions:
    - Native Tool Calling: Model autonomously decides WHEN to query MongoDB (no hardcoded prompts)
    - Structured Outputs: Pydantic response_schema guarantees valid, audit-ready JSON
    - System Instruction Separation: Role loaded from prompts/supervisor_system_prompt.md
    - Audit Trail: Every tool invocation is captured in tool_calls_made
    - Two-Phase Analysis:
        Phase A — Preloaded policies (from external vector search) → skip tool call
        Phase B — Autonomous tool calling → model calls search_policies natively
    """

    def __init__(self):
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.0-flash"
        self.system_instruction = _load_system_prompt()
        self._mongo = None  # Lazy-loaded on first tool call

    def _get_mongo(self):
        """Lazy-load MongoDB utils to avoid import-time connection errors."""
        if self._mongo is None:
            from memory.mongo_utils import MongoUtils
            self._mongo = MongoUtils()
        return self._mongo

    def _search_policies_tool_impl(self, query: str, limit: int = 5) -> str:
        """Native Gemini tool implementation: retrieve relevant policies from MongoDB Atlas.

        Registered as a callable tool — invoked autonomously by the Gemini model
        during the shadow-run simulation when no preloaded policies are provided.
        """
        mongo = self._get_mongo()
        policies = mongo.search_policies(query, limit=limit, use_vector=True)
        logger.info("Tool call: search_policies(query=%r, limit=%d) -> %d results", query, limit, len(policies))
        return json.dumps(policies)

    def _build_tools(self) -> List[Tool]:
        """Register search_policies as a native Gemini callable tool."""
        return [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="search_policies",
                        description=(
                            "Search regulatory policies from MongoDB Atlas by keyword query. "
                            "Returns relevant policy documents with category, jurisdiction, "
                            "risk thresholds, and remediation actions."
                        ),
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

    def run_shadow_simulation(
        self,
        claim: dict,
        preloaded_policies: Optional[List[dict]] = None
    ) -> ShadowRunSession:
        """Run a full shadow-run compliance simulation with structured output.

        Two-phase approach:
        - Phase A: If preloaded_policies provided, skip tool call and analyse directly.
        - Phase B: Let Gemini autonomously call search_policies, then drive a
          tool-use loop until the model returns a final structured response.

        Args:
            claim: Insurance claim dict to analyse.
            preloaded_policies: Optional pre-retrieved policy list (bypasses tool call).

        Returns:
            ShadowRunSession: Fully validated Pydantic model with complete audit trail.
        """
        claim_json = json.dumps(claim, indent=2)
        tool_calls_made: List[str] = []

        # ── Phase A: Preloaded policies ───────────────────────────────────────
        if preloaded_policies:
            policies_json = json.dumps(preloaded_policies, indent=2)
            prompt = (
                f"Analyze this insurance claim against the following retrieved policies.\n\n"
                f"CLAIM:\n{claim_json}\n\n"
                f"RETRIEVED POLICIES:\n{policies_json}\n\n"
                f"GUARDRAILS:\n"
                f"- If any required claim field is missing or unclear, set risk_level=HIGH\n"
                f"- If claim_amount > 100000 AND any policy is triggered, do NOT return APPROVE\n"
                f"- Populate triggered_policies with the matching policy_id values\n"
                f"- Return ONLY valid JSON matching the response schema. No markdown."
            )
            tool_calls_made.append("vector_search_policies (external — preloaded)")

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=ShadowRunSession,
                    temperature=0.1,
                ),
            )
            session = ShadowRunSession.model_validate_json(response.text)
            session.tool_calls_made = tool_calls_made
            return session

        # ── Phase B: Autonomous tool-calling loop ────────────────────────────
        prompt = (
            f"Analyze this insurance claim. First, call the search_policies tool "
            f"to retrieve relevant regulatory policies. Then produce a structured "
            f"risk assessment.\n\n"
            f"CLAIM:\n{claim_json}\n\n"
            f"GUARDRAILS:\n"
            f"- Call search_policies with a keyword derived from the claim description\n"
            f"- If any required claim field is missing or unclear, set risk_level=HIGH\n"
            f"- If claim_amount > 100000 AND any policy is triggered, do NOT return APPROVE\n"
            f"- Return ONLY valid JSON matching the response schema. No markdown."
        )

        # Agentic tool-call loop: keep exchanging turns until the model stops
        # issuing tool calls and returns a final structured response.
        contents = [prompt]
        tools = self._build_tools()

        while True:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=tools,
                    temperature=0.1,
                ),
            )

            # Check if the model issued any function calls this turn
            has_tool_calls = False
            tool_results = []

            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        has_tool_calls = True
                        fc = part.function_call
                        fn_name = fc.name
                        fn_args = dict(fc.args) if fc.args else {}

                        if fn_name == "search_policies":
                            query = fn_args.get("query", "compliance")
                            limit = fn_args.get("limit", 5)
                            result_json = self._search_policies_tool_impl(query, limit)
                            tool_calls_made.append(
                                f"search_policies(query={query!r}, limit={limit})"
                            )
                            tool_results.append({
                                "function_response": {
                                    "name": fn_name,
                                    "response": {"result": result_json}
                                }
                            })

            if not has_tool_calls:
                # Model returned final answer — parse structured output
                break

            # Feed tool results back into the conversation for the next turn
            contents = [prompt, response.candidates[0].content, {"parts": tool_results}]

        # Final turn: request structured JSON output now that policies are retrieved
        final_response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents + [
                "Now produce the final structured ShadowRunSession JSON assessment "
                "based on the policies retrieved above. No markdown, no extra text."
            ],
            config=GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=ShadowRunSession,
                temperature=0.1,
            ),
        )

        session = ShadowRunSession.model_validate_json(final_response.text)
        session.tool_calls_made = tool_calls_made
        return session


# ─────────────────────────────────────────────────────────────
# CLI Demo Entry Point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    demo_claim = {
        "claim_id": "CLM-2026-001",
        "claimant_id": "INS-998877",
        "claim_type": "property_damage",
        "claim_amount": 150000.0,
        "incident_date": "2025-06-15",
        "policy_number": "POL-2025-12345",
        "description": (
            "Severe water damage from burst pipe affecting basement and electrical systems. "
            "Claimant requests full replacement including heirloom furniture valued at $45,000."
        ),
        "metadata": {
            "submitter": "claimant",
            "channel": "mobile_app",
            "priority": "high",
            "attachments": ["photo_001.jpg", "repair_estimate.pdf"]
        }
    }

    print("=" * 60)
    print("RegOps Shield — Supervisor Agent (v1.0.0-GA Demo)")
    print("Model: Gemini 2.0 Flash | Mode: Native Tool Calling")
    print("=" * 60)

    agent = SupervisorAgent()
    result = agent.run_shadow_simulation(demo_claim)

    print(f"\n{'='*60}")
    print("SHADOW-RUN RESULT")
    print(f"{'='*60}")
    print(f"Claim ID      : {result.claim_id}")
    print(f"Risk Level    : {result.risk_level}")
    print(f"Risk Score    : {result.risk_score}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Triggered     : {result.triggered_policies}")
    print(f"Tool Calls    : {result.tool_calls_made}")
    print(f"Rationale     : {result.rationale[:200]}...")
    print(f"{'='*60}\n")
