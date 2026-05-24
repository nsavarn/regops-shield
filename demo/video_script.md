# RegOps Shield — 3-Minute Demo Video Script

**Total Duration**: 3:00

---

## 0:00 – 0:30 | Problem & Introduction

> "In regulated industries, autonomous agents can't just act — they need to decide *safely*, with full governance and auditability.
> 
> RegOps Shield solves this with a patent-pending approach: **pre-execution shadow simulation** before any compliance action is taken.
> 
> Built on Gemini, Google Cloud Agent Builder, and MongoDB Atlas MCP."

---

## 0:30 – 1:50 | Live Demo

**Step 1 — Claim Ingestion**
> "We ingest a synthetic insurance claim: $125,000 health claim, international provider, 2 prior claims."

**Step 2 — Policy Retrieval via MongoDB**
> "The supervisor agent calls the `search_policies` tool — retrieving relevant compliance rules from MongoDB Atlas in real time."

**Step 3 — Shadow-Run Output**
> "Gemini runs the shadow simulation. Risk level: HIGH. Score: 78. Three policies triggered."

**Step 4 — Remediation Recommendation**
> "The Remediation Helper maps the risk to an action: 'Require additional documentation + senior review'."

**Step 5 — MongoDB Persistence + Replay**
> "The entire ShadowRunSession — every decision, policy, rationale — is saved to MongoDB Atlas."
> "We run `python main.py --replay` and the full session is reconstructed from memory. Full audit replayability."

---

## 1:50 – 2:30 | Technical Deep Dive

> "Under the hood:
> - **Gemini 1.5 Pro** with structured JSON output + tool calling
> - **MongoDB Atlas** as our MCP memory layer — document store + text index today, vector search ready for Phase 2b
> - **ShadowRunSession** is our core IP artifact: versioned, typed, replayable
> - Guardrails are explicit — hardcoded policy rules prevent hallucinated approvals"

---

## 2:30 – 3:00 | Impact & Close

> "RegOps Shield delivers enterprise-grade pre-execution governance for agentic AI in Financial Services and Insurance.
> 
> Patent-pending. Open source under Apache 2.0.
> 
> Built as a portfolio + IP asset for 2026 leadership positioning in governed agentic AI.
> 
> **RegOps Shield — because governed agents don't just act. They decide safely.**"

---

## Recording Tips
- Use split screen: terminal on left, MongoDB Compass/Atlas on right
- Show Atlas collection updating in real time during `main.py` run
- Keep terminal font large (24pt+) for readability
- Record in 1080p minimum
