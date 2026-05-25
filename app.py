# app.py
# RegOps Shield — FastAPI Microservice (Cloud Run Deployable)

import os
import json
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from agents.supervisor import SupervisorAgent
from agents.audit import AuditPacketGenerator
from agents.remediation import RemediationHelper
from memory.mongo_utils import MongoUtils

load_dotenv()

# Configure logging for Cloud Run stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("regops-shield")

# — Global shared resources —
mongo: Optional[MongoUtils] = None
supervisor: Optional[SupervisorAgent] = None
remediation: Optional[RemediationHelper] = None
audit_generator: Optional[AuditPacketGenerator] = None

def init_agents():
    global mongo, supervisor, remediation, audit_generator
    mongo = MongoUtils()
    supervisor = SupervisorAgent()
    remediation = RemediationHelper()
    audit_generator = AuditPacketGenerator()
    logger.info("RegOps Shield agents initialized")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_agents()
    yield
    logger.info("RegOps Shield shutting down")

app = FastAPI(
    title="RegOps Shield API",
    description="Adaptive Shadow-Run Compliance Orchestrator — Google Cloud Rapid Agent Hackathon 2026",
    version="0.3.0-cloud",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# — Pydantic Request/Response Models —
class ClaimInput(BaseModel):
    claim_id: str
    claimant_id: str
    claim_type: str
    claim_amount: float = Field(ge=0)
    incident_date: str
    policy_number: str
    description: str
    metadata: Optional[Dict[str, Any]] = {}

class PolicyInput(BaseModel):
    policy_number: str
    policy_type: str
    coverage_amount: float
    terms: List[str] = []
    exclusions: List[str] = []
    version: str = "1.0.0"

class SessionResponse(BaseModel):
    session_id: str
    claim_id: str
    risk_level: str
    risk_score: float
    recommendation: str
    rationale: str
    triggered_policies: int
    risk_factors: List[str]
    remediation_suggestion: str
    policy_version: str
    audit_url: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    mongodb_connected: bool

class AuditResponse(BaseModel):
    audit_timestamp: str
    claim_id: str
    session_id: str
    risk_level: str
    risk_score: float
    recommendation: str
    session_snapshot: Dict[str, Any]

# — API Routes —
@app.get("/", tags=["root"])
def root():
    return {"service": "RegOps Shield API", "status": "running", "version": "0.3.0-cloud"}

@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    db_ok = mongo is not None and mongo.client is not None
    try:
        if db_ok:
            mongo.client.admin.command("ping")
    except Exception:
        db_ok = False
    return HealthResponse(
        status="healthy",
        version="0.3.0-cloud",
        timestamp=datetime.utcnow().isoformat() + "Z",
        mongodb_connected=db_ok
    )

@app.post("/api/v1/shadow-run", response_model=SessionResponse, tags=["orchestration"])
def run_shadow_simulation(payload: ClaimInput, policies: Optional[List[PolicyInput]] = None):
    try:
        if supervisor is None or mongo is None:
            raise HTTPException(status_code=503, detail="Agents not initialized")

        claim_dict = payload.model_dump()
        policies_list = [p.model_dump() for p in policies] if policies else None

        # Run shadow simulation via Supervisor Agent (Gemini 2.0 Flash)
        session = supervisor.run_shadow_simulation(claim_dict, policies_list)

        # Save to MongoDB
        session_dict = session.model_dump(exclude_none=True)
        session_id = mongo.save_session(session_dict)
        session.session_id = session_id

        # Apply remediation
        final_remediation = remediation.get_remediation(session) if remediation else None
        if final_remediation:
            session.remediation_suggestion = final_remediation
            mongo.update_session(session_id, {"remediation_suggestion": final_remediation})

        logger.info(f"Shadow run completed for claim {payload.claim_id} | Risk: {session.risk_level}")

        return SessionResponse(
            session_id=str(session_id),
            claim_id=session.claim_id,
            risk_level=session.risk_level,
            risk_score=session.risk_score,
            recommendation=session.recommendation,
            rationale=session.rationale,
            triggered_policies=len(session.triggered_policies),
            risk_factors=session.risk_factors,
            remediation_suggestion=session.remediation_suggestion,
            policy_version=session.policy_version,
        )
    except Exception as e:
        logger.error(f"Shadow run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions/{session_id}", response_model=AuditResponse, tags=["orchestration"])
def get_session(session_id: str):
    if mongo is None:
        raise HTTPException(status_code=503, detail="MongoDB not connected")
    session = mongo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["risk_score"] = float(session.get("risk_score", 0.0))
    return AuditResponse(
        audit_timestamp=datetime.utcnow().isoformat() + "Z",
        claim_id=session.get("claim_id", ""),
        session_id=str(session_id),
        risk_level=session.get("risk_level", "UNKNOWN"),
        risk_score=session.get("risk_score", 0.0),
        recommendation=session.get("recommendation", "PENDING"),
        session_snapshot=session
    )

@app.get("/api/v1/audit/{session_id}", response_model=AuditResponse, tags=["audit"])
def get_audit_packet(session_id: str):
    if mongo is None or audit_generator is None:
        raise HTTPException(status_code=503, detail="Services not initialized")
    session_doc = mongo.get_session(session_id)
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        from pydantic import TypeAdapter
        ta = TypeAdapter(type("Session", (), {}))
        packet = audit_generator.generate(session_doc)
        return AuditResponse(
            audit_timestamp=packet.get("audit_timestamp", ""),
            claim_id=packet.get("claim_id", ""),
            session_id=str(session_id),
            risk_level=packet.get("risk_level", ""),
            risk_score=float(packet.get("risk_score", 0.0)),
            recommendation=packet.get("recommendation", ""),
            session_snapshot=packet
        )
    except Exception as e:
        logger.error(f"Audit packet generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vector-search", tags=["memory"])
def vector_search_policies(query: Dict[str, str] = Field(..., description="Search text")):  
    if mongo is None:
        raise HTTPException(status_code=503, detail="MongoDB not connected")
    search_text = query.get("query", "")
    if not search_text:
        raise HTTPException(status_code=400, detail="Query text is required")
    try:
        results = mongo.vector_search_policies(search_text, limit=5)
        return {
            "query": search_text,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions", tags=["audit"])
def list_sessions(limit: int = 10):
    if mongo is None:
        raise HTTPException(status_code=503, detail="MongoDB not connected")
    try:
        sessions = mongo.list_sessions(limit)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        logger.error(f"Session listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", "8080"))
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
