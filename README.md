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


---

### Core Novelty: 3 Patentable Claims

**Claim 1 — Adaptive Multi-Agent Governance Fabric**: Supervisor Agent dynamically spawns sub-agents (Fraud Investigator, AML Pattern Evolver, RERA/Compliance Auditor, Risk Handoff Validator) with an Explainable Risk Handoff Protocol.

**Claim 2 — Hybrid Memory + Vector Compliance Knowledge Graph**: MongoDB Atlas MCP as unified persistent memory — vector semantic search for regulatory matching, keyword filtering for policy IDs, bidirectional knowledge graph updates without model retraining.

**Claim 3 — Regulated Adaptive Shadow-Run Protocol**: Pre-execution parallel simulation against policy vectors, hash-chained versioned audit packets, full session replay for regulatory examination.

See full analysis: [`PATENTABILITY.md`](PATENTABILITY.md)

### Project Documentation

| Document | Description |
|---|---|
| [`PATENTABILITY.md`](PATENTABILITY.md) | Core novelty claims, Section 3(k) strategy, prior art map, filing recommendation |
| [`STRATEGIC_ALIGNMENT.md`](STRATEGIC_ALIGNMENT.md) | Track recommendation, execution approach, career/IP leverage positioning |
| [`docs/FORM2_Provisional_Draft.md`](docs/FORM2_Provisional_Draft.md) | Provisional patent specification (Indian IPO — Form 2) |
| [`docs/ADR.md`](docs/ADR.md) | Architecture Decision Record (TOGAF-aligned) |
| [`docs/architecture_diagram.md`](docs/architecture_diagram.md) | ASCII flow diagram + ShadowRunSession schema |
| [`demo/video_script.md`](demo/video_script.md) | Timestamped 3-minute demo recording guide |
| [`prompts/supervisor_system_prompt.md`](prompts/supervisor_system_prompt.md) | Gemini reasoning system prompt |

### Hackathon Strategy

**Target**: Google Cloud Rapid Agent Hackathon 2026 — **MongoDB Track** ($5,000 first prize)  
**Deadline**: June 11, 2026 @ 2:00 PM PDT  
**Submission**: Devpost with hosted URL, public GitHub, and 3-minute demo video  
**Strategic Goal**: Portfolio asset + provisional patent filing (Indian IPO Form 2) for AVP/VP/Director-level positioning in 2026

See full strategy: [`STRATEGIC_ALIGNMENT.md`](STRATEGIC_ALIGNMENT.md)
