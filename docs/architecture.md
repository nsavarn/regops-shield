# RegOps Shield — Architecture

> **Version:** 0.1.0 | **Last Updated:** 2025

## Overview

RegOps Shield is an AI-powered regulatory operations platform built for insurance carriers. It automates claim triage, regulatory compliance checking, and remediation recommendations using a multi-agent architecture orchestrated by a FastAPI backend.

```
┌─────────────────────────────────────────────────┐
│            RegOps Shield Platform              │
├─────────────────────────────────────────────────┤
│  FastAPI App (main.py)                         │
│  ├─ /health          (liveness probe)           │
│  ├─ /readiness       (readiness probe)          │
│  ├─ /integrity/{v}   (SHA-256 check)            │
│  └─ /api/v1/*        (agent routers)            │
├─────────────────────────────────────────────────┤
│  Agent Layer (agents/)                        │
│  ├─ SupervisorAgent   orchestrates workflow     │
│  ├─ TriageAgent       classifies claims          │
│  ├─ ComplianceAgent   checks regulations         │
│  └─ RemediationHelper suggests corrective steps  │
├─────────────────────────────────────────────────┤
│  Shared Utilities (utils/)                    │
│  ├─ models.py         Pydantic v2 schemas        │
│  ├─ errors.py         exception hierarchy        │
│  └─ logging_config.py structured JSON logging   │
├─────────────────────────────────────────────────┤
│  Data Layer (data/ + memory/)                 │
│  ├─ claims.json       sample claim payloads      │
│  ├─ policies.json     regulatory policy rules    │
│  └─ mongo_utils.py    MongoDB persistence layer  │
└─────────────────────────────────────────────────┘
```

## Component Details

### FastAPI Application (`main.py`)

- **App factory pattern** via `create_app()` for testability
- **Async lifespan** context manager for startup/shutdown hooks
- **SlowAPI rate limiting** — 60 req/min default, 30 req/min on root
- **CORS middleware** with configurable origins via `ALLOWED_ORIGINS` env var
- **Centralised error handling** with consistent JSON error schema
- **SHA-256 integrity endpoint** for client-side asset verification

### Agent Layer (`agents/`)

| Agent | Responsibility |
|---|---|
| `SupervisorAgent` | Orchestrates the full triage-to-remediation pipeline |
| `TriageAgent` | Classifies claim severity and routing priority |
| `ComplianceAgent` | Validates claim data against regulatory policies |
| `RemediationHelper` | Generates corrective action recommendations |

### Data Models (`utils/models.py`)

All models use **Pydantic v2** with strict validation:

- `InsuranceClaim` — incoming claim payload with SHA-256 integrity hash
- `ComplianceFinding` — individual regulatory finding with severity level
- `ComplianceReport` — aggregated compliance check result
- `HealthResponse` — liveness probe response
- `ReadinessResponse` — readiness probe with dependency checks

### Error Handling (`utils/errors.py`)

Hierarchical exception model:

```
RegOpsError (base)
├── NotFoundError          (404)
├── ValidationFailed       (422)
├── ServiceUnavailableError (503)
├── UnauthorizedError      (401)
└── ForbiddenError         (403)
```

All errors serialize to:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }
  }
}
```

## Deployment

### Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in secrets
uvicorn main:app --reload --port 8080
```

### Docker

```bash
docker build -t regops-shield:local .
docker run -p 8080:8080 --env-file .env regops-shield:local
```

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/regops-shield
gcloud run deploy regops-shield \
  --image gcr.io/PROJECT_ID/regops-shield \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Security

- Non-root Docker user (`appuser`)
- Secrets via environment variables only (never committed)
- Rate limiting on all public endpoints
- SHA-256 integrity verification endpoint
- Input validation via Pydantic v2 strict mode

## Testing

```bash
pytest --cov=. --cov-report=term-missing
```

Test suite covers:
- Health and readiness endpoints
- Agent invocation with mock LLM responses
- Pydantic model validation (valid and invalid payloads)
- Error handler responses
