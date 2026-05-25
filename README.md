# RegOps Shield: Adaptive Shadow-Run Compliance Orchestrator

**Google Cloud Rapid Agent Hackathon 2026 — MongoDB Track**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com)

A multi-agent system that performs **pre-execution shadow simulation** on regulated workflows (insurance claim triage), applies adaptive remediation, and persists replayable audit memory using **MongoDB Atlas MCP**. Now deployed as a production-grade FastAPI microservice on **Google Cloud Run**.

## Patent-Pending Core Innovation
> **Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol** — enabling governed, closed-loop agentic execution with transparent decision traces.

## Demo Flow
1. Claim ingestion (synthetic JSON or REST API)
2. Policy retrieval via MongoDB Atlas (vector search with `text-embedding-004`)
3. Shadow-run risk assessment via **Gemini 2.0 Flash** with native structured outputs
4. Adaptive remediation recommendation
5. Audit packet persistence + replay from MongoDB

## Architecture
```
Client (REST API / CLI)
 └─▶ FastAPI Microservice (app.py) — Google Cloud Run
     └─▶ Supervisor Agent (Gemini 2.0 Flash + Structured Outputs)
         └─▶ search_policies tool (Vector Search)
         └─▶ MongoDB Atlas MCP
             ├── policies (vector index + hybrid search)
             └── shadow_sessions (audit memory)
         └─▶ Remediation Helper
         └─▶ AuditPacketGenerator
         └─▶ SessionResponse (Pydantic)
```
**Core IP Artifact**: `ShadowRunSession` — versioned, structured record enabling hybrid vector search and full workflow replay.

## Tech Stack
| Layer | Technology |
|---|---|
| Reasoning & Orchestration | **Gemini 2.0 Flash** + native Pydantic structured outputs + tool calling |
| Memory & Tools | MongoDB Atlas MCP (document store + Vector Search with `text-embedding-004`) |
| Guardrails | Explicit policy rules + Pydantic validation |
| API & Deployment | **FastAPI** + Uvicorn + Docker + **Google Cloud Run** |
| Orchestration Pattern | Thin supervisor with ShadowRunSession + replay + vector memory |

## Quick Start

### Local Development
```bash
cp .env.example .env
# Edit .env — set GEMINI_API_KEY, MONGODB_URI, GOOGLE_CLOUD_PROJECT_ID
pip install -r requirements.txt
python main.py          # Run shadow simulation
python main.py --replay # Replay last session from MongoDB
```

### API Server (Local)
```bash
python app.py
# Server runs at http://localhost:8080
# Visit http://localhost:8080/docs for OpenAPI/Swagger UI
```

### Docker / Cloud Run
```bash
docker build -t regops-shield .
docker run -p 8080:8080 --env-file .env regops-shield

# Deploy to Google Cloud Run
gcloud run deploy regops-shield --source . --region us-central1 --allow-unauthenticated
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Health check with MongoDB status |
| POST | `/api/v1/shadow-run` | Run shadow simulation on a claim |
| GET | `/api/v1/sessions/{id}` | Retrieve audit session by ID |
| GET | `/api/v1/audit/{id}` | Generate full audit packet |
| POST | `/api/v1/vector-search` | Vector search policies |
| GET | `/api/v1/sessions` | List recent sessions |

### Example Request
```bash
curl -X POST http://localhost:8080/api/v1/shadow-run \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLM-001",
    "claimant_id": "USR-12345",
    "claim_type": "auto",
    "claim_amount": 15000.00,
    "incident_date": "2025-12-15",
    "policy_number": "POL-XYZ789",
    "description": "Vehicle collision at intersection"
  }'
```

## Project Documentation
- **`PATENTABILITY.md`**: Core novelty claims, Section 3(k) strategy, prior art analysis
- **`STRATEGIC_ALIGNMENT.md`**: Hackathon track recommendation and execution plan
- **`docs/FORM2_Provisional_Draft.md`**: Indian IPO provisional patent specification (Form 2)
- **`docs/ADR.md`**: Architecture Decision Record (TOGAF-aligned)
- **`demo/video_script.md`**: 3-minute demo recording guide

## Environment Variables
| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio API key | Yes |
| `GOOGLE_CLOUD_PROJECT_ID` | GCP project ID | Yes |
| `MONGODB_URI` | MongoDB Atlas connection string | Yes |
| `PORT` | Server port (default: 8080 for Cloud Run) | No |
| `LOG_LEVEL` | Python logging level (default: INFO) | No |

See `.env.example` for full list.

## License
Apache License 2.0 — see [LICENSE](LICENSE) for details.

## Team
- **nsavarn** — Principal Engineer & Patent Architect

---
*Built for Google Cloud Rapid Agent Hackathon 2026 (MongoDB Track)*
