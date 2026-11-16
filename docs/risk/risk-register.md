# Risk Register – MedRx Doctor Version

**Document owner:** MedRx team  
**Version:** 1.0  
**Date:** 2026-11-16  
**Status:** Active  
**Related:** Product Technical Specification v1.0 / v1.1, Lab 3 design work

## Purpose
This register identifies, analyses and tracks risks that could affect the delivery, quality or safety of the MedRx Doctor prototype. It is maintained throughout the project.

## Risk evaluation criteria
- **Probability:** Low / Medium / High
- **Impact:** Low / Medium / High (on schedule, quality, or user safety/trust)
- **Score:** Probability × Impact (qualitative)
- **Treatment:** Avoid / Mitigate / Transfer / Accept

## Risk Register

| ID | Risk | Source | Probability | Impact | Score | Owner | Treatment | Mitigation / Notes | Status |
|----|------|--------|-------------|--------|-------|-------|-----------|--------------------|--------|
| R-01 | LLM provider returns HTTP 429 (rate limit) during a check | Free-tier Gemini/Groq quota | High | Medium | High | Backend | Mitigate | Retry with exponential backoff + circuit breaker; graceful DEGRADED message (FR-07). Fallback provider if available. | Open |
| R-02 | Model invents drug information when leaflet is missing (hallucination) | LLM behaviour | Medium | High | High | AI / Backend | Mitigate | Strict RAG grounding; refuse unknown drugs (FR-05); explicit “not found”; no free-form generation outside retrieved context. | Open |
| R-03 | Missed high-risk interaction (false negative) | Incomplete leaflet data or retrieval failure | Low | High | Medium | AI / Domain | Mitigate | Prefer flagging risk when evidence is weak; cite leaflet source for every claim (NFR-02); human review of high-severity results. | Open |
| R-04 | Excessive minor warnings (alert fatigue) | Broad interaction rules | Medium | Medium | Medium | Product | Mitigate | Severity filtering; short summary first; full section on demand (FR-04). User feedback from INT-1. | Open |
| R-05 | Response time exceeds acceptable threshold (>10 s) | Slow LLM or large context | Medium | Medium | Medium | Backend | Mitigate | Limit number of drugs per check; cache frequent leaflets; timeout + DEGRADED path. | Open |
| R-06 | API key exposure or accidental commit of `.env` | Development practice | Low | High | Medium | All | Avoid | `.env` in `.gitignore`; keys only in local environment; no secrets in repository. | Open |
| R-07 | Free-tier quota exhausted before demo / lab deadline | External provider policy | Medium | High | High | Backend | Mitigate | Monitor usage; secondary provider; offline/fake mode for testing (`FAKE_LLM_FAILURES`). | Open |
| R-08 | Incomplete or outdated leaflet data in the store | Data preparation | Medium | Medium | Medium | Data | Mitigate | Use only public/fictional leaflets; document data limitations; clear “not found” for missing entries. | Open |
| R-09 | Scope creep (patient-specific factors, EHR integration, etc.) | Stakeholder requests | Medium | Medium | Medium | Product | Avoid | Explicit Won’t-have list in specification; defer special patient factors to future work. | Open |
| R-10 | Deployment or environment differences between team members | Local setup | Low | Low | Low | All | Mitigate | Documented setup in deployment diagram; shared `.env.example` (no real keys). | Open |

## Risk Matrix (3×3)

| Impact \ Probability | Low | Medium | High |
|----------------------|-----|--------|------|
| **High**             | R-03, R-06 | R-02, R-07 | — |
| **Medium**           | — | R-04, R-05, R-08, R-09 | R-01 |
| **Low**              | R-10 | — | — |

### Legend
- **High** (red zone): requires active mitigation and monitoring.
- **Medium**: mitigation planned, reviewed periodically.
- **Low**: accepted or lightly monitored.

### Visual matrix

![Risk Matrix](risk-matrix.svg)

## Open actions
1. Implement and test the retry + circuit breaker path (R-01, R-07).
2. Add explicit tests for unknown-drug refusal (R-02).
3. Review severity presentation with the team after first prototype (R-04).

## Traceability
- R-01, R-07 → FR-07, guarded_server.py
- R-02 → FR-05, NFR-03
- R-03 → NFR-02
- R-04 → FR-04, INT-1
- R-05 → NFR-01, FR-08

## Review
Next review: after first end-to-end prototype and guarded server exercises.
