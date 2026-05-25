# API_ENDPOINTS.md
# RegOps Shield — OpenAPI 3.0 Endpoint Specification
# Version: 0.4.0-native-tools
# License: Apache 2.0

Base URL: `https://<CLOUD_RUN_URL>/api/v1`  
Local: `http://localhost:8080/api/v1`  
Swagger UI: `http://localhost:8080/docs`  
ReDoc: `http://localhost:8080/redoc`

---

## 1. Root

### GET /
Service metadata and API version info.

**Response (200 OK):**
```json
{
  "service": "RegOps Shield API",
  "status": "running",
  "version": "0.4.0-native-tools",
  "architecture": "Gemini 2.0 Flash + Native Tool Calling + Atlas Vector Search"
}
```

---

## 2. Health

### GET /health
Health check with MongoDB Atlas connection status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.4.0-native-tools",
  "timestamp": "2026-01-15T14:30:00Z",
  "mongodb_connected": true
}
```

**Response (503 Service Unavailable — MongoDB disconnected):**
```json
{
  "status": "degraded",
  "version": "0.4.0-native-tools",
  "timestamp": "2026-01-15T14:30:00Z",
  "mongodb_connected": false
}
```

---

## 3. Shadow-Run Simulation (Core Endpoint)

### POST /api/v1/shadow-run
Run a pre-execution compliance shadow simulation on an insurance claim.
Gemini 2.0 Flash autonomously retrieves policies, evaluates risk, and returns a structured assessment.

**Request Body:**
```json
{
  "claim_id": "CLM-2026-001",
  "claimant_id": "INS-998877",
  "claim_type": "property_damage",
  "claim_amount": 150000.0,
  "incident_date": "2025-06-15",
  "policy_number": "POL-2025-12345",
  "description": "Severe water damage from burst pipe affecting basement and electrical systems.",
  "metadata": {
    "submitter": "claimant",
    "channel": "mobile_app",
    "priority": "high"
  }
}
```

**Optional — Preloaded Policies (bypasses tool retrieval):**
```json
{
  "claim_id": "CLM-2026-001",
  ...,
  "policies": [
    {
      "policy_id": "POL-003",
      "text": "Claim amount senior approval threshold",
      "rule": "If claim_amount > 100000, escalate to senior approval",
      "action": "SENIOR_APPROVAL",
      "severity": "HIGH"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "session_id": "6789abc123def456",
  "claim_id": "CLM-2026-001",
  "risk_level": "HIGH",
  "risk_score": 85.0,
  "recommendation": "REMEDIATE",
  "rationale": "High claim amount triggers senior approval policy. Property damage to electrical systems requires specialist review.",
  "triggered_policies": 2,
  "risk_factors": ["High claim amount (>$100k)", "Electrical system damage", "Heirloom furniture valuation dispute"],
  "remediation_suggestion": "Require additional documentation + senior review",
  "policy_version": "v1.0",
  "tool_calls_made": ["search_policies(query=water damage property, limit=5)"]
}
```

**Response (503 Service Unavailable — Agents not initialized):**
```json
{
  "detail": "Agents not initialized"
}
```

---

## 4. Session Retrieval

### GET /api/v1/sessions/{session_id}
Retrieve a specific shadow-run session for audit replay.

**Path Parameters:**
- `session_id` (string) — MongoDB ObjectID from shadow-run response

**Response (200 OK):**
```json
{
  "audit_timestamp": "2026-01-15T14:35:00Z",
  "claim_id": "CLM-2026-001",
  "session_id": "6789abc123def456",
  "risk_level": "HIGH",
  "risk_score": 85.0,
  "recommendation": "REMEDIATE",
  "session_snapshot": {
    "claim_id": "CLM-2026-001",
    "risk_level": "HIGH",
    "risk_score": 85.0,
    "tool_calls_made": ["search_policies(...)"]
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

---

## 5. Audit Packet

### GET /api/v1/audit/{session_id}
Generate a full human-readable audit packet from a shadow-run session.

**Path Parameters:**
- `session_id` (string) — MongoDB ObjectID

**Response (200 OK):** Same as `/sessions/{id}` with additional audit fields.

---

## 6. Vector Search

### POST /api/v1/vector-search
Semantic search for regulatory policies using Google text-embedding-004 + Atlas Vector Search.

**Request Body:**
```json
{
  "query": "high amount international provider manual review threshold"
}
```

**Response (200 OK):**
```json
{
  "query": "high amount international provider manual review threshold",
  "count": 3,
  "results": [
    {
      "policy_id": "POL-001",
      "text": "High amount international provider manual review",
      "category": "financial_review",
      "jurisdiction": "US",
      "score": 0.92
    }
  ]
}
```

**Response (500 Internal Server Error — Vector index not found):**
Falls back to keyword text search and returns results.

---

## 7. Session Listing

### GET /api/v1/sessions
List recent shadow-run sessions for audit dashboard.

**Query Parameters:**
- `limit` (integer, default: 10) — Number of sessions to return

**Response (200 OK):**
```json
{
  "count": 5,
  "sessions": [
    {
      "_id": "6789abc123def456",
      "claim_id": "CLM-2026-001",
      "risk_level": "HIGH",
      "risk_score": 85.0,
      "recommendation": "REMEDIATE",
      "timestamp": "2026-01-15T14:35:00Z"
    }
  ]
}
```

---

## Error Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad Request (missing required field) |
| 404 | Resource not found |
| 500 | Internal server error |
| 503 | Service unavailable (MongoDB/Gemini connection issues) |

---

## CORS

All endpoints support cross-origin requests from any origin (`*`) with full credentials.

---

## Rate Limits

No rate limits are enforced at the application level. Deploy to Google Cloud Run with quotas as needed for production use.
