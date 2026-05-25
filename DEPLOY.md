# RegOps Shield — Deployment Guide

**Google Cloud Rapid Agent Hackathon 2026 — MongoDB Track**

This guide walks you through deploying RegOps Shield to Google Cloud Run with MongoDB Atlas integration.

---

## Prerequisites

* A Google Cloud project with billing enabled
* Google Cloud SDK (`gcloud`) installed
* MongoDB Atlas cluster (free tier works)
* Google AI Studio API key (for Gemini)

---

## Step 1: Set Up MongoDB Atlas

1. Create a free cluster at [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Add your IP to the network access allowlist (0.0.0.0/0 for testing)
3. Create a database user with read/write access to `regops_shield`
4. Get your connection string
5. Seed the policies collection:

```bash
python -c "import json; from pymongo import MongoClient; \
  client = MongoClient('YOUR_MONGODB_URI'); \
  db = client['regops_shield']; \
  db.policies.insert_many(json.load(open('data/policies.json')))"
```

### Enable Atlas Vector Search

1. In Atlas UI, navigate to your cluster → Collections → `regops_shield.policies`
2. Create a vector search index named `policies_vector_index`:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

---

## Step 2: Get API Keys

1. **Gemini API Key**: Visit [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. **GCP Project ID**: From [console.cloud.google.com](https://console.cloud.google.com)

---

## Step 3: Deploy to Cloud Run

```bash
# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key"
export GOOGLE_CLOUD_PROJECT_ID="your_project_id"
export MONGODB_URI="your_atlas_connection_string"
export ATLAS_CLUSTER_NAME="your_cluster_name"
export ATLAS_DATABASE="regops_shield"

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Authenticate
gcloud auth login
gcloud config set project $GOOGLE_CLOUD_PROJECT_ID

# Deploy
gcloud run deploy regops-shield \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars \
    GEMINI_API_KEY=$GEMINI_API_KEY,\
    GOOGLE_CLOUD_PROJECT_ID=$GOOGLE_CLOUD_PROJECT_ID,\
    MONGODB_URI=$MONGODB_URI,\
    ATLAS_CLUSTER_NAME=$ATLAS_CLUSTER_NAME,\
    ATLAS_DATABASE=$ATLAS_DATABASE
```

---

## Step 4: Verify Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe regops-shield \
  --region us-central1 --format 'value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl $SERVICE_URL/health

# Test shadow-run endpoint
curl -X POST $SERVICE_URL/api/v1/shadow-run \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "TEST-001",
    "claim_type": "health",
    "claim_amount": 125000,
    "incident_date": "2026-05-01",
    "description": "Emergency surgery abroad",\n    "provider_type": "international"
  }'
```

---

## Step 5: Local Development

```bash
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt

# Run API server
python app.py

# Or run CLI demo
python main.py

# Run supervisor directly
python agents/supervisor.py
```

---

## Architecture

```
Client ──curl/Postman/SDK──▶
  Cloud Run Service (app.py / FastAPI)
    ├── /health         → System status
    ├── /api/v1/shadow-run → SupervisorAgent
    ├── /api/v1/vector-search → MongoUtils.vector_search
    ├── /api/v1/sessions → Session history
    └── /api/v1/audit/{id} → Audit packet

SupervisorAgent ──native tool call──▶ search_policies
  └── MongoUtils.vector_search_policies
      ├── Google text-embedding-004 (embedding)
      └── MongoDB Atlas Vector Search ($vectorSearch)

MongoDB Atlas
  ├── policies (vector index + hybrid search)
  └── shadow_sessions (audit memory)
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `GEMINI_API_KEY not set` | Check `.env` file or Cloud Run env vars |
| Vector search fails | Verify `policies_vector_index` exists in Atlas |
| Connection refused on 8080 | Add `--host 0.0.0.0 --port 8080` to uvicorn |
| `403 Insufficient Permission` | Enable Cloud Build API: `gcloud services enable cloudbuild` |

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
