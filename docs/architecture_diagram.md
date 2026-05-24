# RegOps Shield — Architecture Diagram

## High-Level Flow (TOGAF-Aligned)

```
┌─────────────────────────────────────────────────────────────┐
│                    RegOps Shield                            │
│                                                             │
│  ┌─────────┐     ┌──────────────────────────────────┐      │
│  │  Client │────▶│     Supervisor Agent (Gemini)    │      │
│  │ Request │     │  • Shadow-run simulation         │      │
│  └─────────┘     │  • Guardrail enforcement         │      │
│                  │  • Structured JSON output        │      │
│                  └───────────────┬──────────────────┘      │
│                                  │ search_policies tool     │
│                  ┌───────────────▼──────────────────┐      │
│                  │     MongoDB Atlas MCP             │      │
│                  │  • policies (text index)          │      │
│                  │  • shadow_sessions (audit memory) │      │
│                  └───────────────┬──────────────────┘      │
│                                  │                          │
│                  ┌───────────────▼──────────────────┐      │
│                  │   Remediation Helper              │      │
│                  │  • Risk-to-action mapping         │      │
│                  └───────────────┬──────────────────┘      │
│                                  │                          │
│                  ┌───────────────▼──────────────────┐      │
│                  │   Audit Packet + Replay           │      │
│                  │  • ShadowRunSession (versioned)   │      │
│                  │  • --replay CLI for governance    │      │
│                  └──────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## ShadowRunSession — Core IP Artifact

```
ShadowRunSession
├── claim_id          (str)      — links back to originating request
├── input_claim       (dict)     — full claim snapshot at decision time
├── retrieved_policies (List)    — policies evaluated (replayable)
├── risk_level        (Literal)  — LOW / MEDIUM / HIGH
├── risk_score        (float)    — 0-100 weighted heuristic
├── triggered_policies (List)    — specific rules activated
├── recommendation    (Literal)  — APPROVE / REJECT / REMEDIATE
├── rationale         (str)      — human-readable explanation
├── remediation_suggestion (str) — actionable next step
├── session_id        (str)      — MongoDB ObjectId for replay
├── policy_version    (str)      — enables policy evolution tracking
└── risk_factors      (List)     — granular risk contributors
```

## Phase Roadmap

| Phase | Status | Description |
|---|---|---|
| 2a | ✅ Complete | Shadow-run + remediation + MongoDB persistence + replay |
| 2b | 🔄 In Progress | Gemini tool calling + Atlas Vector Search |
| Final | ⏳ Pending | Demo video + Devpost submission + FORM 2 provisional patent |
