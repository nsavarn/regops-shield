# FORM 2 — COMPLETE SPECIFICATION

**The Patents Act 1970 (39 of 1970) & The Patents Rules 2003**

**Title of Invention**: RegOps Shield — Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol for Agentic Compliance Orchestration in Regulated Enterprise Workflows

**Applicant**: Narendra Tiwari, Pune, Maharashtra, India

**Date**: May 2026

**Jurisdiction**: Indian Patent Office

**Filing Type**: Complete Specification (Provisional converted)

---

## 1. FIELD OF INVENTION

This invention relates to a method and system for pre-execution shadow simulation, adaptive remediation handoff, and replayable audit memory persistence in regulated enterprise workflows using a multi-agent architecture. More specifically, it concerns an agentic compliance orchestration system that employs a Supervisor Agent to perform parallel shadow simulations against regulatory and policy vectors before any action is executed, a Remediation Component that is dynamically invoked upon risk detection to provide traceable context and alternative recommendations, and a Hybrid Memory subsystem that maintains persistent, versioned, vector-embedded session records to enable hybrid search, grounding, and full workflow replay.

The invention applies primarily to regulated industries including banking, financial services, insurance (BFSI), healthcare compliance, and enterprise governance, where decisions carry regulatory liability and must be auditable, explainable, and traceable end-to-end.

---

## 2. BACKGROUND OF THE INVENTION

### 2.1 Field of Technology

Modern enterprise software increasingly relies on autonomous or semi-autonomous AI agents to perform reasoning, decision-making, and action execution in workflows that touch regulated data. In sectors such as insurance underwriting, credit decisioning, anti-money laundering (AML) detection, and healthcare claims processing, the consequences of an erroneous or non-compliant action can include regulatory fines, reputational damage, and legal liability.

### 2.2 Limitations of Prior Art

Existing approaches to compliance in agentic AI systems suffer from several critical limitations:

1. **Post-facto Detection**: Most compliance systems operate after an action has been executed, detecting violations only after they have occurred. This reactive approach exposes the enterprise to regulatory penalties before remediation is possible.

2. **Black-Box Decisioning**: AI systems often produce decisions without explainable reasoning trails, making it impossible to reconstruct the rationale behind a compliance determination during audit or regulatory inquiry.

3. **Fragmented Memory**: Session state, policy references, and audit logs are typically stored in disconnected systems (e.g., separate databases for transactions, logs, and documents), preventing unified replay of decision contexts.

4. **Static Policy Binding**: Compliance rules are typically hardcoded or manually updated, lacking the ability to dynamically retrieve and bind relevant policy vectors at runtime for context-aware enforcement.

5. **Absence of Shadow Simulation**: No existing system performs a parallel "shadow run" — simulating the outcome of an action against policy vectors before the action is committed — as a standard pre-execution step.

### 2.3 Specific Technical Problem

The core technical problem addressed by this invention is: how to build an agentic orchestration system that performs pre-execution shadow simulations of regulatory and policy outcomes, provides explainable handoffs when risks are detected, and maintains a versioned, replayable audit memory that serves as a single source of truth for compliance governance — all within a multi-agent architecture that operates on live, regulated enterprise workflows.

---

## 3. SUMMARY OF THE INVENTION

### 3.1 Object of the Invention

The primary objects of this invention are:

1. To provide a pre-execution shadow simulation engine that evaluates proposed actions against retrieved regulatory policy vectors before any action is committed to production systems.

2. To provide an Explainable Risk Handoff Protocol that generates human-readable and machine-verifiable decision trees when risk thresholds are exceeded, including traceable remediation recommendations.

3. To provide a Hybrid Memory subsystem using MongoDB Atlas as a Single Source of Truth for both persistent policy vector embeddings and versioned session documents, enabling hybrid (vector + keyword) search and full workflow replay.

4. To provide a multi-agent orchestration architecture where a Supervisor Agent dynamically coordinates shadow simulations, policy retrieval, and remediation handoffs without requiring hardcoded execution flows.

5. To provide bidirectional memory updates where synthetic compliance scenarios generated during shadow runs are fed back into the compliance knowledge graph for continuous improvement.

### 3.2 Overview of the System

The system comprises the following principal components:

**A. Supervisor Agent (Phase B: Agentic Extraction Processor)**
- Performs parallel shadow simulations against regulatory and policy vectors
- Uses Gemini 2.0 Flash with native tool calling and structured Pydantic outputs
- Operates as a thin orchestration layer, avoiding complex multi-agent frameworks
- Generates structured JSON output conforming to the ShadowRunSession schema

**B. Policy Extraction Agent**
- Transforms raw regulatory circulars, acts, or compliance documents into structured ComplianceConstraint JSON documents
- Generates vector embeddings for policy clauses and stores them in MongoDB Atlas
- Enforces Human-in-the-Loop (HITL) routing for ambiguous or high-risk clauses before MongoDB promotion
- Implements a 5-stage pipeline: Clause Deconstruction, Schema Mapping, Risk Vector Generation, Remediation Logic, and Ambiguity Guardrail

**C. Remediation Component**
- Dynamically invoked upon risk detection during shadow simulation
- Maps risk vectors to actionable remediation steps (e.g., KYC escalation, additional documentation request, claim rejection)
- Produces traceable context linking the detected risk to the recommended action
- Supports multiple remediation strategies based on severity and policy weight

**D. Hybrid Memory Subsystem (MongoDB Atlas MCP)**
- Persistent policy store with vector embeddings using Google text-embedding-004
- Versioned shadow session documents (ShadowRunSession objects) for audit replay
- Text index for Phase 2a, upgraded to Atlas Vector Search for Phase 2b
- MCP (Model Context Protocol) server exposing search_policies and vector_search_policies as native tools
- Hash-chained versioned documents enabling deterministic audit replay

**E. Audit Packet Generator**
- Produces full human-readable audit packets from shadow-run sessions
- Links session_id back to the originating claim request
- Captures tool_calls_made field recording every tool invocation for compliance replay
- Supports --replay CLI flag for governance audit workflows

### 3.3 Novel Combinations

The novelty of the invention resides in the following combinations, none of which are disclosed in the prior art as a unified system:

1. **Shadow-Run Simulation Engine** combined with **Explainable Risk Handoff Protocol** operating as a pre-execution gate within a regulated workflow.

2. **Hybrid Memory using MongoDB Atlas** serving simultaneously as a policy vector store, session audit store, and MCP tool provider — creating a Single Source of Truth for agentic compliance decisions.

3. **Native Gemini Tool Calling** with **Pydantic Structured Outputs** ensuring valid JSON compliance session records are produced autonomously by the model, with a complete audit trail of tool invocations.

4. **5-Stage Policy Extraction Pipeline** with HITL routing for ambiguous clauses, generating vector embeddings before MongoDB Atlas promotion.

5. **Bidirectional Feedback Loop** where synthetic outcomes from shadow simulations update risk profiles and compliance knowledge graphs in real-time.

---

## 4. DETAILED DESCRIPTION OF THE INVENTION

### 4.1 Overall System Architecture

The system is implemented as a FastAPI microservice deployed on Google Cloud Run, with the following architectural layers:

**Layer 1: Client Interface**
- REST API endpoints (OpenAPI 3.0 specification)
- CLI interface for audit replay operations
- Accepts insurance claim JSON payloads via POST /api/v1/shadow-run

**Layer 2: API Gateway (FastAPI on Google Cloud Run)**
- Route: /api/v1/shadow-run (POST) — initiates shadow simulation
- Route: /api/v1/sessions/{session_id} (GET) — retrieves session for audit
- Route: /api/v1/audit/{session_id} (GET) — generates audit packet
- Route: /api/v1/vector-search (POST) — semantic policy search
- Route: /api/v1/sessions (GET) — lists recent sessions
- Route: /health (GET) — health check with MongoDB status

**Layer 3: Supervisor Agent (agents/supervisor.py)**
- Gemini 2.0 Flash model with native tool calling
- Pydantic ShadowRunSession schema as response_schema
- Two-phase analysis: (1) policy retrieval via tools, (2) structured evaluation with guardrails
- System instruction defines the agent role outside of the prompt
- Audit trail via tool_calls_made field tracking every tool invocation

**Layer 4: Policy Extraction Agent (agents/policy_extractor.py)**
- Transforms unstructured regulatory documents into ComplianceConstraint JSON
- Pydantic models: ComplianceConstraint, ExtractedPolicy, HITLQueueItem
- 5-stage pipeline:
  - Stage 1: Clause Deconstruction — parses regulatory text into atomic clauses
  - Stage 2: Schema Mapping — maps clauses to ComplianceConstraint fields
  - Stage 3: Risk Vector Generation — produces vector embeddings using Google text-embedding-004
  - Stage 4: Remediation Logic — generates remediation_suggestion per constraint
  - Stage 5: Ambiguity Guardrail — flags ambiguous clauses for HITL review
- ingest_policy() pipeline function orchestrates the flow

**Layer 5: MCP Server (agents/mcp_server.py)**
- Exposes MongoDB Atlas as a tool provider via Model Context Protocol
- Tools: search_policies (keyword), vector_search_policies (semantic)
- Enables autonomous model-driven policy retrieval during shadow runs

**Layer 6: Memory Subsystem (memory/mongo_utils.py)**
- MongoDB Atlas connection via MONGODB_URI
- Collections:
  - policies: regulatory policy documents with vector embeddings
  - shadow_sessions: versioned ShadowRunSession audit records
- Vector search index: policies_vector_index (768 dimensions, cosine similarity)
- Text index for Phase 2a keyword search

**Layer 7: Remediation Helper (agents/remediation.py)**
- Maps risk_level and triggered_policies to remediation_suggestion
- Generates audit_packet with full context for compliance review
- Supports risk escalation to human reviewers via HITLQueueItem

### 4.2 ShadowRunSession Schema (Core IP Artifact)

The ShadowRunSession Pydantic model defines the structured compliance session record. This schema is the central intellectual property artifact of the invention:

```python
class ShadowRunSession(BaseModel):
    claim_id: str                       # Links to originating request
    input_claim: dict                   # Full claim snapshot at decision time
    retrieved_policies: List[dict]      # Policies evaluated (replayable)
    risk_level: Literal["LOW","MEDIUM","HIGH"]
    risk_score: float                   # 0-100 weighted heuristic
    triggered_policies: List[str]       # Specific rules/policy_ids activated
    recommendation: Literal["APPROVE","REJECT","REMEDIATE"]
    rationale: str                      # Human-readable explanation
    remediation_suggestion: Optional[str]
    session_id: Optional[str]           # MongoDB ObjectId for replay
    policy_version: Optional[str]       # Enables policy evolution tracking
    risk_factors: Optional[List[str]]   # Granular risk contributors
    evidence_summary: Optional[str]     # Consolidated evidence
    tool_calls_made: Optional[List[str]] # Audit trail of tool invocations
```

This schema ensures:
- **Type safety**: All fields are strongly typed via Pydantic
- **Replayability**: session_id links the record back to the original request
- **Audit trail**: tool_calls_made captures every model tool invocation
- **Versioning**: policy_version tracks policy schema evolution
- **Explainability**: rationale provides human-readable reasoning

### 4.3 Shadow-Run Simulation Process

The shadow-run simulation follows this sequence:

**Step 1: Claim Ingestion**
The API receives an insurance claim JSON with fields: claim_id, claimant_id, claim_type, claim_amount, incident_date, policy_number, description, and metadata.

**Step 2: Policy Retrieval (Parallel to Shadow Run)**
- Option A (Autonomous): The Gemini model autonomously calls the search_policies tool with a keyword derived from the claim description.
- Option B (Preloaded): Vector search via POST /api/v1/vector-search retrieves relevant policies, which are passed to the agent.

**Step 3: Shadow Simulation**
The Supervisor Agent performs a parallel evaluation of the claim against retrieved policies, producing a ShadowRunSession with:
- risk_level (LOW/MEDIUM/HIGH)
- risk_score (0-100)
- triggered_policies (list of policy_ids)
- recommendation (APPROVE/REJECT/REMEDIATE)
- rationale (explainable reasoning)

**Step 4: Guardrail Enforcement**
- If any required claim field is missing: risk_level = HIGH
- If claim_amount > 100,000 AND any policy is triggered: recommendation ≠ APPROVE
- Model must return valid JSON matching the Pydantic schema

**Step 5: Remediation Handoff (if risk detected)**
- If risk_level is MEDIUM or HIGH, the Remediation Component is invoked.
- remediation_suggestion is populated with actionable next steps.
- For HIGH risk or HITL-ambiguous cases, a HITLQueueItem is created.

**Step 6: Memory Commit**
The ShadowRunSession is persisted to MongoDB Atlas in the shadow_sessions collection with:
- Full claim context
- Retrieved policies
- Risk assessment
- Tool call audit trail

**Step 7: Audit Packet Generation**
A human-readable audit packet is generated, linking session_id to the originating claim and capturing all decision context for compliance replay.

### 4.4 Policy Extraction Pipeline (5-Stage Process)

The Policy Extraction Agent transforms raw regulatory documents through the following pipeline:

**Stage 1 — Clause Deconstruction**
Input: Raw regulatory text (e.g., RBI circular, IRDAI guideline, SEC rule)
Output: Atomic clause nodes with paragraph boundaries
Method: Gemini-powered text segmentation identifying independent regulatory assertions.

**Stage 2 — Schema Mapping**
Input: Atomic clause nodes
Output: ComplianceConstraint Pydantic objects
Fields mapped: constraint_id, constraint_type, jurisdiction, applicability_conditions, threshold_values, citations.

**Stage 3 — Risk Vector Generation**
Input: ComplianceConstraint objects
Output: Vector embeddings (768 dimensions, Google text-embedding-004)
Storage: MongoDB Atlas 'policies' collection with policies_vector_index

**Stage 4 — Remediation Logic**
Input: ComplianceConstraint with vector embedding
Output: remediation_suggestion per constraint, including severity-weighted action paths.

**Stage 5 — Ambiguity Guardrail**
Input: ComplianceConstraint with confidence score
Output: If confidence < threshold, create HITLQueueItem for human review.
If confidence >= threshold, promote to MongoDB Atlas production collection.

### 4.5 Guardrails and Safety Mechanisms

The system implements multiple layers of guardrails:

**Pre-Execution Guardrails:**
- Claim field validation before shadow simulation
- Policy retrieval validation (must retrieve at least one policy)
- Risk score bounds enforcement (0-100)

**Runtime Guardrails:**
- Native tool calling: model decides when to query MongoDB (no hardcoded prompts)
- Structured outputs: Pydantic response_schema guarantees valid JSON
- System instruction separation: role defined outside of prompt for consistency

**Post-Execution Guardrails:**
- Audit packet generation with full context
- Session replay capability via session_id lookup
- HITL routing for ambiguous or high-risk classifications

**Section 3(k) Avoidance (Indian Patents Act):**
The invention overcomes the "computer programme per se" exclusion by demonstrating specific technical effects:
- Quantifiable reduction in audit latency through pre-execution validation
- Reduction in regulatory breach incidents via shadow-run prevention
- Deterministic, replayable decision trails via versioned session documents
- Integration of hardware/software: MongoDB Atlas (persistent storage), Google Cloud Agent Builder / Gemini (reasoning), FastAPI (API layer), Cloud Run (deployment)

---

## 5. CLAIMS

### 5.1 Independent Claims

**CLAIM 1:** A computer-implemented system for pre-execution compliance shadow simulation in regulated enterprise workflows, comprising:

(a) a Supervisor Agent executing on a processor, configured to perform parallel shadow simulations of proposed actions against retrieved regulatory policy vectors before said actions are committed to production systems;

(b) a policy retrieval module, coupled to said Supervisor Agent, configured to autonomously retrieve relevant regulatory policies from a hybrid memory subsystem using at least one of keyword search and semantic vector search;

(c) a remediation component, dynamically invoked upon detection of risk thresholds being exceeded during said shadow simulation, configured to generate traceable remediation recommendations linking detected risks to actionable next steps;

(d) a hybrid memory subsystem comprising a persistent document store with vector embeddings, configured to store both regulatory policy documents with vector embeddings and versioned shadow-run session records, enabling hybrid search and full workflow replay;

(e) an audit packet generator configured to produce human-readable audit packets from shadow-run sessions, linking each session to its originating request via a session identifier;

wherein said Supervisor Agent produces a structured compliance session record conforming to a predefined schema, said record comprising: a claim identifier, an input claim snapshot, retrieved policies, a risk level, a risk score, triggered policies, a recommendation, a human-readable rationale, a remediation suggestion, a session identifier, a policy version, and an audit trail of tool invocations.

**CLAIM 2:** A method for agentic compliance orchestration, comprising:

(a) receiving, via an API endpoint, a regulated workflow request comprising claim data;
(b) invoking a policy extraction pipeline that transforms unstructured regulatory documents into structured compliance constraints with vector embeddings;
(c) performing a pre-execution shadow simulation by evaluating said claim data against retrieved regulatory policy vectors using a generative AI model with native tool calling;
(d) enforcing guardrails during said shadow simulation, including: validation of required claim fields, bounds enforcement on risk scores, and prohibition of approval recommendations when claim amounts exceed thresholds and policies are triggered;
(e) generating an explainable risk handoff when risk thresholds are exceeded, producing human-readable and machine-verifiable decision trees;
(f) committing a versioned shadow-run session record to a hybrid memory subsystem;
(g) generating an audit packet linking said session record to the originating request;

wherein said method operates on regulated enterprise workflows in industries selected from the group consisting of: banking, financial services, insurance, healthcare compliance, and enterprise governance.

### 5.2 Dependent Claims

**CLAIM 3:** The system of CLAIM 1, wherein said hybrid memory subsystem employs MongoDB Atlas as a Single Source of Truth, and wherein said vector embeddings are generated using a text-embedding model with at least 768 dimensions and cosine similarity.

**CLAIM 4:** The system of CLAIM 1, wherein said Supervisor Agent employs a generative AI model configured with:
(a) native tool calling enabling autonomous policy retrieval decisions;
(b) structured output schema ensuring valid JSON compliance session records;
(c) system instruction defining agent role separated from runtime prompts;
wherein said tool calling produces an audit trail field recording every tool invocation for compliance replay.

**CLAIM 5:** The system of CLAIM 1, further comprising a policy extraction agent implementing a multi-stage pipeline comprising:
(a) clause deconstruction parsing regulatory text into atomic clause nodes;
(b) schema mapping converting said atomic clause nodes into structured compliance constraint objects;
(c) risk vector generation producing vector embeddings for said compliance constraint objects;
(d) remediation logic generating remediation suggestions per constraint;
(e) ambiguity guardrail routing low-confidence constraints to human-in-the-loop review;
wherein said pipeline enforces HITL routing for ambiguous clauses before promotion to a production policy collection.

**CLAIM 6:** The system of CLAIM 1, wherein said remediation component maps risk levels and triggered policies to remediation suggestions selected from the group consisting of: KYC escalation, additional documentation request, claim rejection, manual review routing, and policy exception request.

**CLAIM 7:** The system of CLAIM 1, wherein said structured compliance session record further comprises a policy_version field enabling policy schema evolution tracking across time, and a risk_factors field capturing granular risk contributors.

**CLAIM 8:** The system of CLAIM 2, wherein said API endpoint is implemented as a FastAPI microservice deployed on a cloud computing platform, and wherein said generative AI model is selected from the group consisting of: Gemini 2.0 Flash, Gemini 1.5 Pro, and compatible large language models with native tool-calling capabilities.

**CLAIM 9:** The system of CLAIM 5, wherein said ambiguity guardrail evaluates a confidence score generated during schema mapping, and creates a HITLQueueItem for constraints with confidence scores below a configurable threshold, said HITLQueueItem comprising the constraint data, the confidence score, and the reason for ambiguity.

**CLAIM 10:** The system of CLAIM 1, wherein said system is deployed as a microservice on Google Cloud Run with Docker containerization, and wherein said hybrid memory subsystem is exposed as a Model Context Protocol (MCP) server providing search_policies and vector_search_policies as callable tools to said Supervisor Agent.

**CLAIM 11:** A computer-readable storage medium having stored thereon instructions which, when executed by one or more processors, cause said processors to perform the method of CLAIM 2.

**CLAIM 12:** The system of CLAIM 1, wherein said system further comprises bidirectional memory update capabilities, wherein synthetic compliance scenarios generated during shadow simulations are fed back into a compliance knowledge graph stored in said hybrid memory subsystem to enable continuous improvement of policy vector embeddings and risk assessment accuracy.

---

## 6. ABSTRACT

A computer-implemented system and method for pre-execution compliance shadow simulation in regulated enterprise workflows. The system comprises a Supervisor Agent that performs parallel shadow simulations of proposed actions against regulatory policy vectors before actions are committed to production systems. A policy retrieval module autonomously retrieves relevant regulatory policies using keyword or semantic vector search. A remediation component is dynamically invoked upon risk detection to generate traceable remediation recommendations. A hybrid memory subsystem using MongoDB Atlas stores both regulatory policy documents with vector embeddings and versioned shadow-run session records, enabling hybrid search, grounding, and full workflow replay. The system produces structured compliance session records (ShadowRunSession) with complete audit trails including tool invocation histories. An Explainable Risk Handoff Protocol generates human-readable and machine-verifiable decision trees when risk thresholds are exceeded. A multi-stage policy extraction pipeline transforms raw regulatory documents into structured compliance constraints with HITL routing for ambiguous clauses. The invention overcomes the exclusion under Section 3(k) of the Indian Patents Act 1970 by demonstrating specific technical effects including quantifiable reduction in audit latency, pre-execution risk prevention, and deterministic replayable decision trails through hardware-software integration.

---

## 7. DRAWINGS

### FIG. 1: High-Level System Architecture (TOGAF-Aligned)

The architecture comprises seven layers:

```
+---------------------------------------------------------------+
|  CLIENT LAYER                                                 |
|  +---------------------------------------------------------+  |
|  | REST API / CLI Interface                                |  |
|  +---------------------------------------------------------+  |
+-----------------------------^-------------------------------+
                              | HTTP / JSON
+-----------------------------v-------------------------------+
|  API GATEWAY (FastAPI on Google Cloud Run)                  |
|  /api/v1/shadow-run, /api/v1/sessions, /api/v1/audit,       |
|  /api/v1/vector-search, /health                             |
+-----------------------------^-------------------------------+
                              | Request Routing
+-----------------------------v-------------------------------+
|  SUPERVISOR AGENT (agents/supervisor.py)                    |
|  Gemini 2.0 Flash + Native Tool Calling + Pydantic Schema   |
|  ShadowRunSession: claim_id, risk_level, recommendation...  |
+------------------+------------+------------------------------+
                   |            |
         search_policies       structured output
         tool call             (JSON)
                   v            v
+------------------+------------+------------------------------+
|  MCP SERVER (agents/mcp_server.py)                            |
|  Exposes MongoDB Atlas as tool provider                       |
|  Tools: search_policies, vector_search_policies               |
+------------------+------------+------------------------------+
                   |            |
         keyword search        vector search
                   v            v
+------------------+------------+------------------------------+
|  MEMORY SUBSYSTEM (MongoDB Atlas)                             |
|  Collections:                                                 |
|  - policies (text index + vector index)                       |
|  - shadow_sessions (versioned audit records)                  |
+------------------+------------+------------------------------+
                   |
         remediation / HITL
                   v
+------------------+------------+------------------------------+
|  REMEDIATION HELPER (agents/remediation.py)                   |
|  Risk-to-action mapping, Audit Packet Generator               |
|  HITLQueueItem creation for ambiguous cases                   |
+---------------------------------------------------------------+
```

### FIG. 2: ShadowRunSession — Core IP Artifact Schema

```
ShadowRunSession
+-- claim_id (str)           : Links to originating request
+-- input_claim (dict)       : Full claim snapshot at decision time
+-- retrieved_policies (List): Policies evaluated (replayable)
+-- risk_level (Literal)     : LOW / MEDIUM / HIGH
+-- risk_score (float)       : 0-100 weighted heuristic
+-- triggered_policies (List): Specific policy_ids activated
+-- recommendation (Literal) : APPROVE / REJECT / REMEDIATE
+-- rationale (str)          : Human-readable explanation
+-- remediation_suggestion   : Actionable next step
+-- session_id (str)         : MongoDB ObjectId for replay
+-- policy_version (str)     : Policy schema evolution tracking
+-- risk_factors (List)      : Granular risk contributors
+-- evidence_summary         : Consolidated evidence
+-- tool_calls_made (List)   : Audit trail of tool invocations
```

### FIG. 3: Policy Extraction Pipeline — 5-Stage Flow

```
Stage 1: Clause Deconstruction
  Input:  Raw regulatory text (RBI circular, IRDAI guideline)
  Output: Atomic clause nodes with paragraph boundaries
  Method: Gemini-powered text segmentation

Stage 2: Schema Mapping
  Input:  Atomic clause nodes
  Output: ComplianceConstraint Pydantic objects
  Fields: constraint_id, constraint_type, jurisdiction,
          applicability_conditions, threshold_values, citations

Stage 3: Risk Vector Generation
  Input:  ComplianceConstraint objects
  Output: Vector embeddings (768 dims, text-embedding-004)
  Storage: MongoDB Atlas 'policies' collection

Stage 4: Remediation Logic
  Input:  ComplianceConstraint with vector embedding
  Output: remediation_suggestion per constraint

Stage 5: Ambiguity Guardrail
  Input:  ComplianceConstraint with confidence score
  Output: HITLQueueItem (if confidence < threshold) OR
          MongoDB production promotion (if confidence >= threshold)
```

### FIG. 4: Shadow-Run Simulation Sequence

```
Client                    API Gateway              Supervisor Agent         MongoDB Atlas
  |                           |                        |                        |
  |--- POST /shadow-run ----> |                        |                        |
  |                           |--- forward claim -----> |                        |
  |                           |                        |--- search_policies ---> |
  |                           |                        |                        |--- query policies
  |                           |                        |<-- policies ----------- |                        |
  |                           |                        |--- evaluate claim -----> |
  |                           |                        | (shadow simulation)      |
  |                           |                        |--- commit session -----> |
  |                           |                        |                        |--- save ShadowRunSession
  |                           |                        |<-- session_id --------- |
  |                           |<-- ShadowRunSession -- |                        |
  |<-- JSON response -------- |                        |                        |
```

---

## 8. PRIOR ART AVOIDANCE MAP

### 8.1 What This Invention Is NOT

The following prior art categories are explicitly distinguished from this invention:

1. **Basic Fraud Detection Chatbots**: Systems that perform post-facto fraud detection or classification using simple rule engines or LLM classifiers. This invention performs pre-execution shadow simulation before any action is taken.

2. **Post-Facto Reporting Tools**: Compliance dashboards and audit log viewers that report on historical actions. This invention prevents non-compliant actions before they occur through shadow-run validation.

3. **Simple RAG (Retrieval-Augmented Generation) Systems**: Systems that retrieve documents and generate responses. This invention adds pre-execution shadow simulation, explainable handoff protocols, and versioned replayable audit memory.

4. **Generic LLM Classifiers**: Systems that classify inputs without structured reasoning or audit trails. This invention produces structured ShadowRunSession records with complete audit trails (tool_calls_made), versioned policy tracking, and explainable rationale.

5. **Standalone Policy Engines**: Systems that evaluate rules without agentic orchestration or adaptive remediation. This invention coordinates a multi-agent architecture with dynamic reasoning and HITL integration.

### 8.2 What This Invention IS

The invention is a multi-agent system characterized by the following novel combinations:

1. **Shadow-Run Engine**: Validates actions against policy vectors before they occur, operating as a pre-execution gate in regulated workflows.

2. **Single Source of Truth**: MongoDB Atlas MCP provides unified memory for both policy vector embeddings and versioned session documents, eliminating fragmented storage.

3. **Immutable Traces**: Hash-chained versioned ShadowRunSession documents enable deterministic audit replay, with session_id linking every record to its originating request.

4. **Explainable Risk Handoff Protocol**: Replaces black-box decisioning with explicit, human-readable, and machine-verifiable decision trees. Each risk detection produces a traceable remediation_suggestion.

5. **Native Tool Calling with Structured Outputs**: Gemini 2.0 Flash with Pydantic response_schema guarantees valid JSON session records, while autonomous tool calling decisions create an audit trail of every tool invocation.

6. **5-Stage Policy Extraction Pipeline with HITL**: A novel pipeline that transforms unstructured regulatory text into structured compliance constraints, with ambiguity guardrails routing uncertain clauses to human review before production promotion.

### 8.3 Prior Art Comparison Table

| Feature | Prior Art (Chatbots/RAG) | This Invention (RegOps Shield) |
|---------|-------------------------|-------------------------------|
| Execution Timing | Post-facto detection | Pre-execution shadow simulation |
| Decision Trace | Opaque / untraceable | Explainable Risk Handoff Protocol |
| Memory | Disconnected stores | MongoDB Atlas as Single Source of Truth |
| Audit | Log files (non-replayable) | Versioned ShadowRunSession with replay |
| Policy Binding | Static / hardcoded | Dynamic vector + keyword retrieval |
| Remediation | None or post-hoc | Dynamic, traceable handoff protocol |
| Agent Architecture | Single LLM or chatbot | Multi-agent with Supervisor + Extraction + Remediation |
| Section 3(k) Status | Likely excluded (software per se) | Overcomes via technical effects + HW/SW integration |

---

## 9. SECTION 3(k) ANALYSIS (INDIAN PATENTS ACT 1970)

### 9.1 Statutory Exclusion

Section 3(k) of the Indian Patents Act 1970 excludes "a mathematical or business method or a computer programme per se or algorithms" from patentability. This invention addresses the exclusion through the following technical effect arguments.

### 9.2 Technical Effects Overcoming 3(k)

**Effect 1: Quantifiable Reduction in Audit Latency**
The pre-execution shadow simulation reduces audit latency by identifying compliance risks before actions are committed. This produces a measurable technical improvement in the regulatory compliance workflow, reducing the time between action and audit from days/weeks to milliseconds.

**Effect 2: Pre-Execution Risk Prevention**
By validating actions before execution, the system prevents regulatory breaches at the point of decision, rather than detecting them post-facto. This represents a specific technical improvement in the reliability of regulated workflow systems.

**Effect 3: Deterministic Replayable Decision Trails**
The versioned ShadowRunSession schema with session_id linking and tool_calls_made audit fields enables deterministic replay of every decision context. This is a specific technical contribution to the field of compliance audit systems, enabling reproducible audit reconstructions.

**Effect 4: Closed-Loop Compliance Feedback**
Bidirectional memory updates feed synthetic compliance scenarios from shadow runs back into the knowledge graph, improving policy vector accuracy and risk assessment over time. This adaptive feedback loop represents a specific technical improvement in compliance governance systems.

### 9.3 Hardware/Software Integration

The invention is not a "computer programme per se" but a system integrating:

- **Hardware**: MongoDB Atlas cluster (persistent storage layer), Google Cloud Run infrastructure (compute layer), client devices (API endpoints)
- **Software**: FastAPI microservice, Gemini 2.0 Flash (reasoning + tool calling), Pydantic schema validation, MCP server protocol
- **Network**: REST API endpoints, MongoDB connection protocols, Google Cloud networking
- **Result**: A governed agentic orchestration system that produces regulated enterprise compliance outcomes

This combination of hardware and software components working together to produce a specific technical result (compliance governance with pre-execution validation and replayable audit) brings the invention outside the scope of Section 3(k) exclusion.

### 9.4 Case Law Support

The invention aligns with the Indian Patent Office guidelines for computer-related inventions, which permit patentability when:
1. The invention demonstrates a technical effect beyond normal program execution
2. The invention integrates hardware and software components
3. The invention solves a technical problem (here: pre-execution compliance validation and audit replay)

---

## 10. REDUCTION TO PRACTICE

### 10.1 Repository Evidence

The invention has been reduced to practice as demonstrated by the following artifacts in the GitHub repository (nsavarn/regops-shield):

**Core Implementation Files:**
- `agents/supervisor.py` — Supervisor Agent with Gemini 2.0 Flash, native tool calling, Pydantic structured outputs, ShadowRunSession schema
- `agents/policy_extractor.py` — Policy Extraction Agent with 5-stage pipeline (Clause Deconstruction, Schema Mapping, Risk Vector Generation, Remediation Logic, Ambiguity Guardrail)
- `agents/mcp_server.py` — MCP Server exposing MongoDB Atlas as a tool provider
- `agents/remediation.py` — Remediation Helper with risk-to-action mapping and audit packet generation
- `memory/mongo_utils.py` — MongoDB Atlas utilities for policy search, vector search, and session persistence
- `app.py` — FastAPI microservice with OpenAPI 3.0 endpoints
- `main.py` — CLI entry point for demo execution

**Data Files:**
- `data/claims.json` — Synthetic insurance claim test data
- `data/policies.json` — Synthetic regulatory policy documents for seeding MongoDB

**Documentation Files:**
- `README.md` — System overview, tech stack, demo flow, architecture
- `PATENTABILITY.md` — Patentability analysis and prior art avoidance
- `STRATEGIC_ALIGNMENT.md` — Hackathon track strategy and career positioning
- `API_ENDPOINTS.md` — OpenAPI 3.0 endpoint specification (v0.4.0-native-tools)
- `DEPLOY.md` — Deployment guide for Google Cloud Run + MongoDB Atlas
- `docs/ADR.md` — Architecture Decision Record with 4 ADRs (Core Architecture, Policy Retrieval, Patent Wedge, Demo Scenario)
- `docs/architecture_diagram.md` — ASCII architecture diagrams (Layers, ShadowRunSession schema, Policy Pipeline, Sequence)
- `prompts/supervisor_system_prompt.md` — Supervisor system prompt with 5-step extraction flow

### 10.2 Demo Scenario

The implementation demonstrates the following workflow:

1. **Insurance Claim Triage**: A synthetic insurance claim (property damage, $150,000) is submitted via POST /api/v1/shadow-run
2. **Policy Retrieval**: The Supervisor Agent autonomously calls search_policies tool to retrieve relevant regulatory policies
3. **Shadow Simulation**: The claim is evaluated against policies, producing a ShadowRunSession with risk_level=HIGH, risk_score=78, recommendation=REMEDIATE
4. **Remediation Handoff**: remediation_suggestion populated with actionable escalation path
5. **Memory Commit**: Session persisted to MongoDB Atlas with full audit trail
6. **Audit Replay**: Session retrieved via GET /api/v1/sessions/{session_id} for compliance review

### 10.3 Phase Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 2a | Complete | Shadow-run + remediation + MongoDB persistence + replay |
| 2b | In Progress | Gemini native tool calling + Atlas Vector Search |
| Final | Pending | Demo video + Devpost submission + FORM 2 patent filing |

### 10.4 Public Timestamp

The GitHub repository at https://github.com/nsavarn/regops-shield serves as a public timestamp for the invention, with 26 commits documenting the development progression. The repository license is Apache 2.0.

---

## 11. APPLICANT DETAILS

**Name**: Narendra Tiwari (Narendra Savarn)
**Address**: Pune, Maharashtra, India
**Profession**: Principal AI Enterprise Platform Solution Architect
**Nationality**: Indian

---

## 12. DECLARATION

The complete specification described herein is based on the provisional specification filed under The Patents Act 1970. The invention as described in this complete specification represents the full disclosure of the subject matter, including all embodiments, variations, and improvements developed since the provisional filing.

The applicant declares that the invention is new, involves an inventive step, and is capable of industrial application within the meaning of Sections 2(1)(j), 2(1)(ja), and 2(1)(ac) of The Patents Act 1970.

**Signature**

_________________________
Narendra Tiwari
Applicant
May 2026

---

*END OF COMPLETE SPECIFICATION*
