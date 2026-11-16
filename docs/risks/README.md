# Risks – MedRx Doctor version

## Risk Register

| ID | Risk | Probability | Impact | Score | Owner | Treatment | Source |
|----|------|-------------|--------|-------|-------|-----------|--------|
| R-01 | LLM returns incorrect interaction (hallucination) | Medium | High | High | Team | Guardrail: only answer from leaflet store; refuse unknown drugs | INT-1 / FR-05 |
| R-02 | Free-tier API rate limit (HTTP 429) during demo | High | Medium | High | Team | Retry + circuit breaker + safe fallback message | Lab 1 / FR-07 |
| R-03 | User trusts a false positive / false negative | Medium | High | High | Team | Always show leaflet quote + severity; explicit disclaimer | INT-1 |
| R-04 | Leaflet data incomplete or outdated | Medium | Medium | Medium | Team | Clear "not found" instead of inventing; limited demo dataset | DEC-2 |
| R-05 | Response time exceeds acceptable limit (>10s) | Medium | Medium | Medium | Team | Limit number of drugs; timeout on LLM calls | INT-1 / NFR-01 |
| R-06 | Team member unavailable before deadline | Low | Medium | Low | Team | Task split + shared GitHub repo | Organization |
| R-07 | PlantUML / diagram tools not available for review | Low | Low | Low | Team | Images embedded in README | Design |

## Risk Matrix (3x3)

| Impact \ Probability | Low | Medium | High |
|----------------------|-----|--------|------|
| **High** |  | R-01, R-03 |  |
| **Medium** | R-06 | R-04, R-05 | R-02 |
| **Low** | R-07 |  |  |

### Legend
- **High** (red): needs active treatment before demo
- **Medium** (yellow): monitor + mitigation in place
- **Low** (green): accepted

## Notes
- Treatments map to guardrails that will be specified in the AI failure modes document.
- Owners can be refined after team discussion.
- Matrix uses the 3-level scale from Lab 3.
