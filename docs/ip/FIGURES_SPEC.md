# RegOps Shield - Drawing Specifications for FIG. 1 to FIG. 6

This document defines IPO-compliant line-drawing specifications for the six figures referenced in the Complete Specification (FORM 2). It is intended for use by a patent draughtsman or designer to prepare A4 black-and-white drawings for filing.

## General IPO Drawing Requirements

- **Paper size:** A4 (210 mm x 297 mm)
- **Margins:** Top 2.54 cm, Bottom 2.54 cm, Left 1.8 cm, Right 1.8 cm
- **Style:** Black line drawings on white background, no greyscale or colour
- **Text:** Typed labels only, no handwriting
- **Reference numerals:** Use exactly the numerals defined below (102, 104, ... 608)
- **One figure per sheet**, with "FIG. X" centered at the bottom margin

---

## FIG. 1 - Overall System Architecture

**Purpose:** Depicts the major subsystems of RegOps Shield and their data flows.

### Reference Numerals

| Numeral | Name                                      |
| :------ | :---------------------------------------- |
| 102     | Workflow Ingestion Subsystem              |
| 104     | Shadow-Run Execution Engine               |
| 106     | Hybrid Governance Memory Repository       |
| 108     | Vector Index                              |
| 110     | Structured Document Store                 |
| 112     | Policy Retrieval Engine                   |
| 114     | Risk Evaluation Engine                    |
| 116     | Adaptive Remediation Engine               |
| 118     | Explainable Memory Handoff Subsystem      |
| 120     | Retroactive Replay Validation Subsystem   |
| 122     | Self-Healing Regulatory Ingestion Subsystem|
| 124     | Runtime Security & Isolation Layer        |
| 126     | Shadow AI Discovery Component             |

### Layout Specification

- Place **Workflow Ingestion Subsystem (102)** at the top centre as a rectangle.
- Draw a downward arrow from 102 to **Shadow-Run Execution Engine (104)**.
- From 104, draw arrows to separate rectangles for:
  - Policy Retrieval Engine (112)
  - Risk Evaluation Engine (114)
  - Adaptive Remediation Engine (116)
  - Explainable Memory Handoff Subsystem (118)
- Below these, draw a large rectangle labelled **Hybrid Governance Memory Repository (106)**.
  - Inside 106, draw two smaller rectangles:
    - **Vector Index (108)**
    - **Structured Document Store (110)**
- Connect 112, 114, 116, and 118 to 106 with arrows.
- Draw **Retroactive Replay Validation Subsystem (120)** and **Self-Healing Regulatory Ingestion Subsystem (122)** as rectangles below or beside 106, each connected to 106.
- At the lower right, draw **Runtime Security & Isolation Layer (124)** and beneath or beside it **Shadow AI Discovery Component (126)**, connected to the main flow.
- Place numerals next to each box: e.g., "Workflow Ingestion Subsystem (102)".

---

## FIG. 2 - Pre-Execution Shadow-Run Simulation Process

**Purpose:** Shows the sequence of interactions between an autonomous agent, the governance fabric, and a human reviewer.

### Reference Numerals

| Numeral | Step Description                            |
| :------ | :------------------------------------------ |
| 202     | Receive workflow request                    |
| 204     | Request policies & history                  |
| 206     | Execute steps in sandbox                    |
| 208     | Annotate with risk scores                   |
| 210     | Invoke remediation                          |
| 212     | Construct replayable governance memory object|
| 214     | Execute in production                       |
| 216     | Escalate for human review                   |
| 218     | Block with documented reasons               |

### Layout Specification

- Draw a **sequence diagram** with three vertical swim-lanes:
  - "Autonomous Agent" (left)
  - "Governance Memory Fabric" (centre)
  - "Human Reviewer" (right)
- Draw lifelines (vertical dashed lines) for each entity.
- Show horizontal arrows:
  - From Autonomous Agent to Governance Memory Fabric:
    - "202 - Receive workflow request"
    - "204 - Request policies & history"
    - "206 - Execute steps in sandbox"
    - "208 - Annotate with risk scores"
    - "210 - Invoke remediation"
  - From Governance Memory Fabric back to Autonomous Agent:
    - "212 - Construct replayable governance memory object"
  - From Autonomous Agent to Governance Memory Fabric:
    - "214 - Execute in production"
  - From Autonomous Agent to Human Reviewer:
    - "216 - Escalate for human review"
  - From Governance Memory Fabric to Autonomous Agent:
    - "218 - Block with documented reasons"
- Place the reference numerals (202, 204, etc.) next to each arrow.

---

## FIG. 3 - Replayable Governance Memory Object

**Purpose:** Defines the internal fields of the replayable governance memory object.

### Reference Numerals

| Numeral | Field Description                                           |
| :------ | :--------------------------------------------------------- |
| 302     | Workflow identifier                                        |
| 304     | Workflow type                                              |
| 306     | Input parameters & contextual attributes                   |
| 308     | Policy versions & regulatory bases applied                 |
| 310     | Runtime execution trace (prompts, tool calls, code, events)|
| 312     | Execution trace graph (steps, risk, decisions)             |
| 314     | Remediation actions taken or recommended                   |
| 316     | Trust & confidence scores for agent outputs                |
| 318     | Escalation events & reviewer annotations                   |
| 320     | Timestamps & digital signatures for auditability           |

### Layout Specification

- Draw one large rectangle titled: "Replayable Governance Memory Object"
- Inside, draw horizontal lines to split it into rows.
- In each row, put the numeral at the left and the field name to the right, e.g.:

```text
+--------------------------------------------+
| Replayable Governance Memory Object        |
+--------------------------------------------+
| 302  Workflow identifier                   |
| 304  Workflow type                         |
| 306  Input parameters & context            |
| 308  Policy versions & regulatory bases    |
| 310  Runtime execution trace               |
| 312  Execution trace graph                 |
| 314  Remediation actions                   |
| 316  Trust & confidence scores             |
| 318  Escalation events & annotations       |
| 320  Timestamps & digital signatures       |
+--------------------------------------------+
```

---

## FIG. 4 - Self-Healing Regulatory Ingestion Pipeline

**Purpose:** Shows the end-to-end self-healing pipeline from regulation ingestion to promotion or human review.

### Reference Numerals

| Numeral | Step Description                                 |
| :------ | :----------------------------------------------- |
| 402     | Receive new regulation                           |
| 404     | Ingest content                                   |
| 406     | Extract constraints & embeddings                 |
| 408     | Store in staging area                            |
| 410     | Select historical sessions                       |
| 412     | Replay under new constraints                     |
| 414     | Compute governance drift scores                  |
| 416     | Detection phase                                  |
| 418     | Diagnosis phase                                  |
| 420     | Healing phase                                    |
| 422     | Learning phase                                   |
| 424     | Adversarial test harness                         |
| 426     | Atomic promotion to active policy set            |
| 428     | Flag for human review                            |

### Layout Specification

- Use process rectangles and decision diamonds.
- Top-to-bottom flow:
  - 402 -> 404 -> 406 -> 408 -> 410 -> 412 -> 414
- From 414, branch into a loop with:
  - 416 (Detection) -> 418 (Diagnosis) -> 420 (Healing) -> 422 (Learning) -> back to 416.
- From 414, also connect into:
  - 424 (Adversarial test harness)
- After 424, draw a decision diamond:
  - "Drift & tests acceptable?"
    - Yes -> 426 (Atomic promotion to active policy set)
    - No -> 428 (Flag for human review)
- Ensure numerals are placed inside or next to each box/diamond.

---

## FIG. 5 - Explainable Memory Handoff and Human Escalation

**Purpose:** Shows how the replayable governance memory object is handed off from AI to a human reviewer and recorded back.

### Reference Numerals

| Numeral | Step Description                                          |
| :------ | :-------------------------------------------------------- |
| 502     | Generate replayable governance memory object             |
| 504     | Pass to human reviewer dashboard                         |
| 506     | Inspect full execution trace & reasoning lineage         |
| 508     | Provide decision (approve, modify, or reject)            |
| 510     | Record outcome & rationale as new case in governance memory|

### Layout Specification

- Draw a **swim-lane diagram** with two vertical lanes:
  - "Autonomous Agent"
  - "Human Reviewer"
- In the Autonomous Agent lane:
  - Box: "502 - Generate replayable governance memory object"
  - Arrow to Human Reviewer lane: "504 - Pass to human reviewer dashboard"
- In the Human Reviewer lane:
  - Box: "506 - Inspect full execution trace & reasoning lineage"
  - Arrow back to Autonomous Agent lane: "508 - Provide decision (approve, modify, or reject)"
- In the Autonomous Agent lane:
  - Box: "510 - Record outcome & rationale as new case in hybrid governance memory"
- Place numerals next to the corresponding boxes/arrows.

---

## FIG. 6 - Shadow AI Discovery Component and Governance Routing

**Purpose:** Shows how unmanaged AI endpoints are discovered and routed into governed shadow-run workflows.

### Reference Numerals

| Numeral | Step Description                                           |
| :------ | :--------------------------------------------------------- |
| 602     | Monitor telemetry, configuration data & traffic patterns   |
| 604     | Detect unmanaged/unauthorized AI agent or LLM endpoint     |
| 606     | Route subsequent requests through workflow ingestion for shadow-run|
| 608     | Generate alert & governance incident record                |

### Layout Specification

- Draw four rectangles vertically, with arrows between them:
  - Top: "602 - Monitor telemetry, configuration data & traffic patterns"
  - Next: "604 - Detect unmanaged/unauthorized AI agent or LLM endpoint"
  - Next: "606 - Route subsequent requests through workflow ingestion subsystem for governed shadow-run simulation"
  - Bottom: "608 - Generate alert & governance incident record"
- Optional decision diamond after 604:
  - "Registered with ingestion subsystem?"
    - Yes -> arrow back to "Monitoring (602)" or annotation "Already governed"
    - No -> arrow to 606
- Use clean arrows; all outlines in black.

---

## Conversion to Filing-Ready Drawings

1. Open Draw.io, Visio, PowerPoint, or similar.
2. Set page size to A4 and margins as specified above.
3. Create one page per figure and replicate the layouts.
4. Add reference numerals exactly as defined.
5. Export each page to PDF and combine into `Drawings_RegOpsShield.pdf`.

This specification must be kept in sync with the Complete Specification
(especially claim numerals and description references).
