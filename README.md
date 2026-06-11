# RegOps Shield: Adaptive Shadow-Run Compliance Orchestrator

**Google Cloud Rapid Agent Hackathon 2026 — MongoDB Track**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com)

## Overview

**RegOps Shield** is a multi-agent system designed for **pre-execution shadow simulation** on regulated workflows — such as insurance claim triage — with adaptive remediation and replayable audit memory. Built on **Gemini 2.0 Flash** with native tool calling, **MongoDB Atlas MCP** for persistent memory and vector search, and deployed as a production-grade FastAPI microservice on **Google Cloud Run**.

## Key Features

| Feature | Description |
|---------|-------------|
| **Shadow-Run Simulation** | Pre-execution risk assessment against policy vectors before any compliance action |
| **Multi-Agent Orchestration** | Supervisor + Remediation + Audit agents working in concert |
| **MongoDB Atlas MCP** | Document store + Vector Search (768-dim, text-embedding-004) + Hybrid Search |
| **Structured Outputs** | Pydantic-validated `ShadowRunSession` schema for deterministic JSON |
| **Audit Trail** | Full session replayability from MongoDB with SHA-256 integrity |
| **HITL Governance** | Human-in-the-loop escalation for high-risk decisions |

## Demo Flow

1. **Claim Ingestion** — Synthetic JSON or REST API (`POST /api/v1/shadow-run`)
2. **Policy Retrieval** — MongoDB Atlas Vector Search with Gemini `text-embedding-004`
3. **Shadow-Run Assessment** — Gemini 2.0 Flash with native structured outputs
4. **Remediation** — Adaptive recommendation based on triggered policies
5. **Persistence** — Audit packet stored in MongoDB for full replay
6. **Replay** — `python main.py --replay` reconstructs the entire session

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Reasoning & Orchestration** | Gemini 2.0 Flash + Native Tool Calling + Pydantic Structured Outputs |
| **Memory & Tools** | MongoDB Atlas MCP (Document Store + Atlas Vector Search) |
| **Guardrails** | Explicit policy rules + Pydantic validation |
| **API & Deployment** | FastAPI + Uvicorn + Docker + Google Cloud Run |
| **Embeddings** | Google `text-embedding-004` (768-dim) |

## Quick Start

### Local Development

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env: set GEMINI_API_KEY, MONGODB_URI, GOOGLE_CLOUD_PROJECT_ID

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run shadow simulation CLI
python main.py

# 4. Replay last session
python main.py --replay
```

### API Server

```bash
# Start server (default: http://localhost:8080)
python app.py

# View Swagger UI
open http://localhost:8080/docs
```

### Cloud Run Deployment

```bash
gcloud run deploy regops-shield --source . --allow-unauthenticated
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info and version |
| `/health` | GET | Health check with MongoDB status |
| `/api/v1/shadow-run` | POST | Run shadow simulation (ClaimInput) |
| `/api/v1/sessions/{id}` | GET | Retrieve audit session |
| `/api/v1/audit/{id}` | GET | Generate full audit packet (SHA-256) |
| `/api/v1/vector-search` | POST | Semantic policy search |
| `/api/v1/sessions` | GET | List recent sessions |

## MCP Server (Model Context Protocol)

Implements `agents/mcp_server.py` exposing MongoDB Atlas as a tool provider for Gemini:

| Tool | Description |
|------|-------------|
| `search_policies` | Keyword-based policy retrieval |
| `vector_search_policies` | Semantic search using Atlas Vector Search |
| `health_check` | Connection probe |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google AI Studio API key | Yes |
| `GOOGLE_CLOUD_PROJECT_ID` | GCP project ID | Yes |
| `MONGODB_URI` | MongoDB Atlas connection string | Yes |
| `ATLAS_CLUSTER_NAME` | Atlas cluster name | Yes |
| `ATLAS_DATABASE` | Database name (default: `regops_shield`) | Yes |
| `GOOGLE_EMBEDDING_MODEL` | Embedding model (default: `text-embedding-004`) | Optional |
| `VECTOR_INDEX_NAME` | Vector search index name (default: `policies_vector_index`) | Optional |
| `PORT` | Server port (default: `8080`) | Optional |
| `LOG_LEVEL` | Logging level (default: `INFO`) | Optional |

## Seed Sample Data

Data is located in `data/` (claims.json, policies.json). Seed MongoDB via:

```bash
python -c "import json; from pymongo import MongoClient; \
client = MongoClient('$MONGODB_URI'); \
db = client['regops_shield']; \
db.policies.insert_many(json.load(open('data/policies.json')))"
```

## Project Structure

```
regops-shield/
├── agents/
│   ├── __init__.py
│   ├── audit.py          # Audit packet generator (SHA-256)
│   ├── mcp_server.py     # MongoDB Atlas MCP tool provider
│   ├── policy_extractor.py  # Policy extraction agent
│   ├── remediation.py    # Remediation action engine
│   └── supervisor.py     # Supervisor agent (Gemini 2.0 Flash)
├── memory/
│   └── mongo_utils.py    # MongoDB utilities + Vector Search
├── prompts/
│   └── supervisor_system.yaml  # Agent system instructions
├── data/
│   ├── claims.json       # Synthetic insurance claims
│   └── policies.json     # Compliance policy rules
├── demo/
│   └── video_script.md   # 3-minute demo video script
├── docs/
│   ├── ADR.md            # Architecture Decision Records
│   └── architecture_diagram.md
├── .env.example          # Environment template
├── app.py                # FastAPI microservice
├── main.py               # CLI entry point
├── requirements.txt      # Production dependencies
├── Dockerfile            # Cloud Run container
├── DEPLOY.md             # Deployment guide
├── API_ENDPOINTS.md      # API documentation
├── LICENSE               # Apache 2.0
└── README.md             # This file
```

## Documentation

- **[API Endpoints](API_ENDPOINTS.md)** — Full API documentation with request/response examples
- **[Deployment Guide](DEPLOY.md)** — Cloud Run deployment and troubleshooting
- **[Architecture Decisions](docs/ADR.md)** — Key technical decisions and rationale
- **[Architecture Diagram](docs/architecture_diagram.md)** — System architecture overview

## Compliance Checklist

| Requirement | Status |
|-------------|--------|
| Gemini 2.0 Flash with native tool calling | ✅ |
| MongoDB Atlas Vector Search + text-embedding-004 | ✅ |
| Google Cloud Run deployment ready | ✅ |
| Multi-agent architecture with HITL governance | ✅ |
| Immutable audit trail with SHA-256 integrity | ✅ |
| Production FastAPI microservice | ✅ |
| Pydantic-validated structured outputs | ✅ |
| Apache 2.0 open-source license | ✅ |

## License

[Apache 2.0](LICENSE) — Built for the Google Cloud Rapid Agent Hackathon 2026.
