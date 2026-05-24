# Architecture Decision Record — RegOps Shield

## ADR-001: Core Architecture Pattern

**Decision**: Thin supervisor orchestration with structured Gemini output + MongoDB Atlas as memory/tool layer

**Context**: Hackathon deadline June 11, 2026. Need functional, demo-ready agent within 18 days.

**Rationale**:
- Thin orchestration avoids complex multi-agent frameworks that introduce fragility
- ShadowRunSession Pydantic model as first-class entity ensures type safety and replayability
- MongoDB Atlas provides both document persistence and vector search readiness in one MCP

**Alternatives Rejected**:
- LangChain/LangGraph: Adds dependency risk and steep learning curve
- Full function calling with dynamic spawning: Over-engineered for hackathon scope
- RERA-specific India domain rules: Narrows global appeal for Financial Services track judges

---

## ADR-002: Policy Retrieval Strategy

**Decision**: Text index (Phase 2a) → Atlas Vector Search (Phase 2b)

**Context**: Need fast policy retrieval; vector search adds patent novelty.

**Rationale**: Start simple and stable; vector search can be layered without breaking the core flow.

---

## ADR-003: Patent Wedge Language

**Invention Title**: Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol

**Core Claims**:
1. Pre-execution shadow simulation of policy/risk outcomes before agent action
2. Dynamic remediation handoff with traceable context on risk detection
3. Versioned, vector-embedded session documents in MongoDB for hybrid search, grounding, and replay

---

## ADR-004: Demo Scenario Selection

**Decision**: Insurance Claim Triage (synthetic data only)

**Rationale**: Universally understood regulated workflow; no live API dependencies; judges in Financial Services track immediately grasp the value.
