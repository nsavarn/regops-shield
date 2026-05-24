# FORM 2 — PROVISIONAL SPECIFICATION
## The Patents Act 1970 (39 of 1970) & The Patents Rules 2003

**Title of Invention**: RegOps Shield — Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol for Agentic Compliance Orchestration in Regulated Enterprise Workflows

**Applicant**: Narendra Tiwari, Pune, Maharashtra, India

**Date**: May 2026

---

## Field of Invention

The present invention relates to autonomous AI agent systems, and more particularly to a method and system for pre-execution shadow simulation, adaptive remediation handoff, and replayable audit memory persistence in regulated enterprise workflows using a multi-agent architecture.

---

## Background

Existing autonomous agent systems in regulated industries (Financial Services, Insurance) make decisions post-facto — acting first and auditing afterward. This creates compliance risk, regulatory exposure, and a lack of traceable governance. Current solutions lack:

1. Pre-execution validation before irreversible agent actions
2. Traceable, explainable handoff protocols between agents
3. Versioned, replayable audit memory for compliance review
4. Closed-loop self-improving compliance knowledge graphs

---

## Objects of the Invention

1. To provide a system for pre-execution shadow simulation of regulated workflow actions
2. To enable adaptive remediation handoff with traceable, explainable context
3. To persist versioned, vector-embedded session records enabling hybrid search, grounding, and full workflow replay
4. To demonstrate concrete technical improvement in compliance assurance and decision traceability for autonomous agents

---

## Summary of Invention

The invention discloses a **Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol** comprising:

- A **Supervisor Agent** using an AI language model with tool-calling and multi-step reasoning capabilities to perform pre-execution shadow simulations of proposed actions against regulatory and policy vectors stored in a hybrid vector-document database
- Upon detection of risk, the supervisor dynamically invokes a **remediation component** (invoked as a secondary agent or tool) passing traceable context and least-disruptive remediation alternatives
- All reasoning steps, retrievals, decisions, and handoffs are persisted as **versioned, vector-embedded documents** enabling hybrid semantic and keyword-based search, full workflow replay, and human-verifiable audit packets
- **Bidirectional memory updates**: agents write back synthetic outcomes to the compliance knowledge graph enabling continuous improvement without model retraining
- **Guardrails layer**: pre/post-action validation, risk thresholds, and human escalation triggers ensuring responsible agentic execution

---

## Claims (Draft)

**Claim 1** (Independent): A computer-implemented system for governed agentic compliance orchestration, comprising:
(a) a supervisor agent employing an AI language model platform with tool-calling and multi-step reasoning to perform pre-execution parallel shadow simulations of proposed workflow actions against a policy knowledge base;
(b) a remediation component, invoked as a secondary agent or tool upon risk detection, receiving traceable handoff context and generating least-disruptive remediation alternatives;
(c) a hybrid vector-document database storing all simulation steps, handoffs, and decisions as versioned, structured session records;
(d) a replay mechanism enabling full workflow reconstruction from persisted session records.

**Claim 2** (Dependent on 1): The system of Claim 1, wherein the hybrid vector-document database employs both semantic vector search and keyword-based text search for policy retrieval and session grounding.

**Claim 3** (Dependent on 1): The system of Claim 1, wherein each session record includes versioned vector embeddings, enabling semantic similarity search across historical compliance decisions.

**Claim 4** (Dependent on 1): The system of Claim 1, further comprising a guardrails layer implementing pre-action validation rules, risk score thresholds, and human escalation triggers.

**Claim 5** (Dependent on 1): The system of Claim 1, wherein agents perform bidirectional memory updates — writing synthetic compliance outcomes back to the knowledge graph for continuous self-improvement without external model retraining.

---

## Abstract

A system and method for pre-execution shadow simulation of regulated agentic workflows, comprising a supervisor agent that simulates policy outcomes before action, dynamically hands off to remediation components upon risk detection with traceable context, and persists all decisions as versioned, vector-embedded documents in a hybrid database (e.g., MongoDB Atlas) for replay, audit, and continuous improvement. The system addresses the 2026 governance gap in autonomous agent auditability in regulated enterprise domains.

---


*Note: This is a provisional specification.*

---

### Section 3(k) Avoidance Strategy (Indian Patents Act, 1970)

#### Context
Section 3(k) of the Indian Patents Act, 1970, excludes "a computer programme per se" from patentability. The Guidelines for Computer-Related Inventions (CRIs) issued by the Indian Patent Office (2016, revised 2017) require a "technical effect" or "technical contribution" beyond the mere execution of software to overcome this exclusion.

#### Strategy
The invention is framed by its specific technical effect within a regulated enterprise workflow, not as a software algorithm in isolation:

1. **Technical Effect in Regulated Enterprise Workflow**
   - Compliance auditability improvement (quantifiable reduction in audit latency)
   - Pre-execution risk prevention (reduction in regulatory breach incidents)
   - Deterministic, replayable decision trails (machine-verifiable traceability)
   - Closed-loop compliance knowledge graph with bidirectional memory updates

2. **Hardware / Software Integration Claim**
   - MongoDB Atlas MCP Server (persistent storage layer with hybrid vector + full-text search)
   - Google Cloud Agent Builder + Gemini (orchestration and reasoning engine)
   - Real-time API integrations with transaction processors and regulatory data feeds
   - The combination of these specific components produces a governed agentic orchestration system with measurable compliance outcomes.

3. **Measurable Technical Improvements**
   - Reduced compliance decisioning latency (shadow-sim before action vs. post-facto detection)
   - Eliminated post-facto audit reconciliation overhead (immutable, hash-chained versioned documents)
   - Continuous risk profile updating without full model retraining (bidirectional synthetic outcome feedback)
   - Deterministic session replay capability for regulatory examination (versioned vector-embedded audit packets)

#### Filing Recommendation
- **Immediate**: File Provisional Specification (Form 2) online via the Indian Patent Office e-filing portal.
- **Core Claim Focus**: "Regulated Adaptive Shadow-Run with Explainable Memory Handoff Protocol" as the primary inventive concept.
- **Within 12 Months**: Convert to Complete Specification following the reduction-to-practice demo video, functional prototype, and audit log evidence bundle.
- **Evidence Bundle**: GitHub repository (public timestamp), demo video, JSON synthetic datasets, MongoDB audit log outputs, Architecture Decision Record (ADR).

---

### Prior Art Avoidance Map

| Prior Art Type | Gap | RegOps Shield Innovation |
|---|---|---|
| Basic fraud detection chatbots | No pre-execution simulation | Shadow-Run Engine validates before action |
| Siloed compliance tools | No unified memory | MongoDB Atlas MCP as single source of truth |
| Post-facto audit systems | No immutable trace | Hash-chained versioned documents with replay |
| Black-box LLM decisions | No human-readable rationale | Explainable Risk Handoff Protocol |
| Standard RAG systems | No bidirectional learning | Synthetic outcome feedback for continuous improvement |

---

### Patentability Assessment Summary

| Criterion | Assessment |
|---|---|
| Novelty | Addresses 2026 agentic AI governance gap — few production examples exist |
| Inventive Step | Closed-loop orchestration with pre-execution shadow simulation + explainable handoff |
| Industrial Applicability | Directly deployable in BFSI (banks, insurers, NBFCs, real-estate escrow) |
| Technical Effect | Pre-execution compliance prevention, immutable audit trails, reduced audit latency |
| Section 3(k) Risk | Mitigated via enterprise integration framing + hardware/software combination claim |
| Filing Strength | Strong — combines agentic AI pattern, persistent memory fabric, and regulatory compliance |

---

### Repo Evidence for Reduction to Practice

| Asset | Location in Repo | Purpose |
|---|---|---|
| Supervisor Agent | `agents/supervisor.py` | Shadow-run simulation logic |
| Remediation Agent | `agents/remediation.py` | Risk-to-action mapping and handoff |
| Audit Generator | `agents/audit.py` | Structured audit packet generation |
| MongoDB Utils | `memory/mongo_utils.py` | Hybrid vector + text search, hash-chained persistence |
| Synthetic Claims | `data/claims.json` | Demo scenarios (LOW / MEDIUM / HIGH risk triggers) |
| Policy Vectors | `data/policies.json` | Compliance rules seeded for vector search |
| System Prompt | `prompts/supervisor_system_prompt.md` | Gemini reasoning instructions |
| ADR | `docs/ADR.md` | TOGAF-aligned architecture decisions |
| Architecture Diagram | `docs/architecture_diagram.md` | Flow diagram + ShadowRunSession schema |
| Video Script | `demo/video_script.md` | Timestamped 3-minute demo recording guide |

---

*Last updated: May 24, 2026 (Grok Strategic Assessment incorporated)*  
*Next Step: File Provisional online via IPO e-filing portal; convert to Complete Specification within 12 months*
*Note: This is a provisional specification. Full specification with drawings, code appendices, and complete claims to be filed within 12 months.*
