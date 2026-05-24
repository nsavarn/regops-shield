# RegOps Shield: Adaptive Shadow-Run Compliance Orchestrator

**Google Cloud Rapid Agent Hackathon 2026 — MongoDB Track**

A functional multi-agent system that performs **pre-execution shadow simulation** on regulated workflows (insurance claim triage), applies adaptive remediation, and persists replayable audit memory using **MongoDB Atlas MCP**.

## Patent-Pending Core Innovation

> **Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol** — enabling governed, closed-loop agentic execution with transparent decision traces.

## Demo Flow

1. Claim ingestion (synthetic JSON)
2. Policy retrieval via MongoDB (text search, vector-ready)
3. Shadow-run risk assessment with built-in guardrails
4. Adaptive remediation recommendation
5. Persist session + replay from audit memory

## Architecture

```
Client Request
    └─▶ Supervisor Agent (Gemini 1.5 Pro)
            └─▶ search_policies tool
                    └─▶ MongoDB Atlas MCP
                            ├── policies  (text index → vector-ready)
                            └── shadow_sessions (audit memory)
            └─▶ Remediation Helper
                    └─▶ Audit Packet + Replay
```

**Core IP Artifact**: `ShadowRunSession` — versioned, structured record enabling hybrid search and full workflow replay.

## Tech Stack

| Layer | Technology |
|---|---|
| Reasoning & Orchestration | Gemini 1.5 Pro + structured JSON output + tool calling |
| Memory & Tools | MongoDB Atlas MCP (document store + text index, vector-ready) |
| Guardrails | Explicit policy rules + Pydantic validation |
| Orchestration Pattern | Thin supervisor with ShadowRunSession + replay capability |

## Quick Start

```bash
cp .env.example .env        # Add GEMINI_API_KEY + MONGODB_URI
pip install -r requirements.txt
python main.py              # Run shadow simulation
python main.py --replay     # Replay last session from MongoDB
```

## Submission Assets

- 3-minute demo video (link to be added)
- Public GitHub: https://github.com/nsavarn/regops-shield
- Provisional Patent (India IPO) — reduction to practice achieved

## Business Value

Delivers enterprise-grade pre-execution governance for agentic AI in Financial Services & Insurance — reducing compliance friction while providing full auditability.

Built as a strategic portfolio + IP asset for 2026 AVP/VP-level positioning.

## License

Apache 2.0 — see [LICENSE](LICENSE)
