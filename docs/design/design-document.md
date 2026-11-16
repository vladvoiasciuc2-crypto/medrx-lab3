# Design Document - MedRx - version D (physician) - v1.0

> **DRAFT for team review.** Written with AI help from the repository content and the team documents; every statement must be checked by both team members before submission. Items marked *(confirm)* are assumptions. The test IDs in section 7 are provisional until the Lab 6 tests exist.

## 0. Document control

| Item | Value |
|---|---|
| Version | 1.0 (draft) |
| Date | 2026-11-17 |
| Authors | MedRx team (VV, MD) |
| Related documents | Product Technical Specification (v1.1 / v1.2 draft), risk register v1.1 ([docs/risk/risk-register.md](../risk/risk-register.md)), AI Use Log |

| Version | Date | Change | Approved by |
|---|---|---|---|
| 1.0 | 2026-11-17 | First complete design document (Lab 3) | *(confirm)* |

## 1. Overview

MedRx (doctor version) is a teaching prototype. A physician enters a list of drugs; the system finds interactions in a leaflet store and shows each one with its severity and a word-for-word leaflet quote. The web UI talks to an orchestrator and an interaction-check agent. The agent reads the leaflet data only through MCP tools (a drug-info server and a leaflet-RAG server over the leaflet store), so the interaction lookup does not depend on what the language model "remembers". A guardrail layer sits in front of the LLM adapter, which is the single place for retries, timeouts, the circuit breaker and the provider choice (Gemini primary, Groq fallback). When the LLM fails, the physician still gets the leaflet quote with a DEGRADED message. A HIGH interaction is held until the physician approves or rejects it; the model can never approve.

![Component diagram](https://kroki.io/plantuml/png/eNplUstOwzAQvPsrVjmBRIXEkQNqlFZpoaFV2sCFyzbZBqupHdkOokL8O2sHlFRc1l7PzD4mmVqHxnWnRjjpGoKMqvwTZrp02sAESn1qtSLloJJYGzwJe5SqRb4N2NadWck17gQGXS8Xgzh6pT0UywjQ8iFaLI9YE0RxzaiN4EvAqFW0NuU7WWeQqwTNOk8Wl5SlcmS4m9QKmFweAX2twE4W8-RJfI_7px2ayqBsoMEz9UXTIs5nY9JqlQFW2HLlN3VlyJnzDZTSlJ10sDeERzLXQcrMeNgiSzZgyXyQ-b9KZbp6ItVB_zKCfJYX6SWtITw05CZ5nI6JnPIeFTrco-VOq54Glo2hwHjZirLRXcUr0kkqCfGmtzmdZ-LvM04evOvFMty8l3APi91uA7fwuF0_i_Dksd65EEPuB2WuX9Bp3dgR5CcdIz737zzQQOotDjHkwTcfepRHnJKq-M_5AScyy5k=)

## 2. UML diagrams

Sources are in [docs/uml/](../uml/). Each diagram lists the requirements (FR / NFR IDs of the specification) it covers.

### 2.1 Use case - covers FR-01 to FR-05, FR-07, FR-09, FR-10, NFR-06
![Use case](https://kroki.io/plantuml/png/eNptkk1PAjEQhu_9FZM9QQwY-RBiCMGAwQNcMHry0uwOUOm20M7yEeN_d7qssiveOjPPOzN925En6ShLtdC4JCALTq3WBIlyGJOyRpAijTDHRMUyJEB6r1hlCBrwhs6H3ARqExuTdXVOplIZyDxCLD16IUMezuUiiGazOWyd3asE3bupTTFVRsEtTJ3d1SMeAYEYDPzJE6bDoQjbSLPiTSJeZXHkMeeOl3Ui-BQQ5oaxED0ZQgeJy1agGcibvo7vysh4jfEGVABlfllfUK0y9bK2B_C4R6foBDegUS41EuwyS1gI2leCZab1L-rPXhZwpww_boMPGNzYWi91wfTKzAI_uMFfpF9GnqVJ2JzMbIw9mPza7KuxBEubmaReaLr_aILTThKyTakiVq3YDeT9AZ3jFy2k9-JLFJY3GsPcykrYqoadatirhn3BAmg2w7kND_zSysQ6S5Cf-lLp5hU8EpqkUri_LoS-fBMR-v2cR1zmr_0NxBPrLA==)

Source: [usecase.puml](../uml/usecase.puml). Use cases: enter drug list (FR-01), check interactions (FR-02), show severity and leaflet quote (FR-03, NFR-02), show full leaflet section (FR-04), handle unknown drug (FR-05, NFR-03), handle LLM rate limit (FR-07, NFR-06), approve proposal and reject proposal (FR-09, FR-10).

### 2.2 Component - covers FR-02, FR-05, FR-07, FR-09 to FR-12, NFR-01, NFR-02, NFR-06
Shown in section 1. Source: [component.puml](../uml/component.puml).

### 2.3 Sequence (critical scenario: check interactions with a failure path and the approval step) - covers FR-02, FR-03, FR-07, FR-08, FR-09, NFR-01, NFR-06
![Sequence](https://kroki.io/plantuml/png/eNqFU01vEzEUvO-veOopEYqoChzoATVKVtugRkQRhWPk7r4kBq-92M9t-feMnd2QhAOX_Zg3bzxvbN8FUV5iawrRYphme65_krbCXtWinQ00oRcte9pF5RuvtAmkbEOq67x7VqZQUZyN7RP7Ah3O09ylV9FBV9e6U1bo6js_0ePiilTA67y0-LsWqR1byaxpdc5azlYU2D-zz2X8ntcfHpakGtVJT8D_OaHiVltN09XBRVUui4NRmnyCJ7olTkao8XEXCgCApxXgOiWyOU1klDnjAmWQkrNb2rFsEgzi1tHbf7uKxJsMop5DNBIIy1sntHXRNr1emiTpWXQKU4htq_xvGiHutpNxYZzrSAm1Lgi9w5cw8EAjaEUr2lDDqjHa8rigrAZRjHsiOnPwZQXlhE-Oi95cX8P6-5uPeH54fS0YppQReKhrDmGQG4YYrL2hWovK0YCSphgiPYwJMKncL6r705MFmBItsfutgObevfRt0P0VnXDmXezV4fQxfHr-wbUctXprfX2DZ-eCMkfiEckdp16nq9X6y7dyDuq6_FzOvpZzcNgExhZl8_8znOhILLfkvTO61QK9LW5N9HwRzrys1tM5FmyRLU5-jvtSfqst3OOSIoc7EHBT_wATyCpD)

Source: [sequence.puml](../uml/sequence.puml). Failure path: retry loop, then the DEGRADED message. Approval step: for a HIGH interaction the physician sees the result and quote, then approves or rejects.

### 2.4 State machine (interaction check with approval) - covers FR-05, FR-07, FR-09
![State machine](https://kroki.io/plantuml/png/eNptkk1PAjEQhu_9FXMUDXjnYDAahQSMH0fjobTDbqW0pDOFv-90WetCvDTt9H2m78x0RqwT551X7NgjLAJj0oZdDGBaNFsYg0gYYadN6wLC1dFxC3q_T_Gg_Uh9Xn_BeHwHC-tRlaU7PRTWhQamYKPhmIDyeueYwDtiVa-L9iMbg0QidX-vE2xiDvZc-RL5qURFmsM2xGMAm3IDtxAiWM36XP6ITdIWi3y5XAmiD9p5vRajv28W2SsGK8h9X5Ko54vn-dBM72UIdZVOISFlz0Bt8XIlLgo6UpcpC3E6dG76lmhTavBoG6R_kXf8RsNDJHURUjXZwAvJwGyWLWm5URWu06ntq5HaoRoJUWadXNMyxM1laxTAKlr0YHQQYf8LcCLxt1zAG6CYk8FTQyZKcCgZ1Ux28st-ANAa0vU=)

Source: [state.puml](../uml/state.puml).

### 2.5 Deployment (lab setup) - covers NFR-04, NFR-05
![Deployment](https://kroki.io/plantuml/png/eNplks1uwjAQhO9-ilVO4QAPwAGR_ihEKlVUoLRHBy_Eqokje0MbVbx71w4tEr0lO99kZ-zMPUlH3dEI0mQQlqhevmAMCltj-yM2BKmRFXikrh2JxiqEZEWdCoqRLdk2AenhKSvhWwAMwJ2znx5dEkcAvEHv5Y4g2WIFmyI6tpuCxfOfp-yptg2kJ2xOo0iU7__88sB7fVSzfH0jLu9LzulO6AaC3yOhJMlKet5hUO4NEniyDiNTPLxdUuw1108mvB3SrCzgA3s_5Hh8fhXnS_Xc2gNzWQHhELSNQB5zXoPkeNSNBv5KcjVqWnTVgC9ueIet9Zoz9YHng4HxeBYKwhQW63XJV2B30tTW00iEcZBD2yk34RAiPIdZaPOr5xfzKk4mk1nowTOHUvnYToRLCwIHmsJBE7Sdr8UcG8U_xA9keKCa)

Source: [deployment.puml](../uml/deployment.puml).

## 3. Design patterns

| Pattern | Problem in our design | Where it appears | Negative consequence |
|---|---|---|---|
| Adapter (+ Strategy for the fallback order) | Free-tier providers (Gemini as primary, Groq as fallback - ADR-0003) have different APIs and can be throttled; the rest of the app should not care which one answers. | LLM adapter component (component + deployment diagrams; sequence diagram: 'LLM adapter' lifeline) | Two providers to configure and test; answers differ a little between models, so tests must not depend on exact wording. |
| Retry with backoff + Circuit Breaker + Timeout | The LLM service returns HTTP 429/5xx or does not answer; the physician needs an answer or a clear message within seconds (NFR-01, FR-07). | Inside the LLM adapter; sequence diagram 'loop at most 3 attempts (or until deadline)'; deployment diagram (external dependency). The circuit breaker is only named in the component diagram, not yet drawn in a flow. | More code and more settings to tune; retries add waiting time that competes with the 10-second limit (ADR-0001 sets a per-attempt timeout T and an overall deadline D; values still to be measured). |
| Human-in-the-loop (approval gate) | The AI may propose a check result, but a physician is legally accountable (INT-7), so only a person can mark a check as reviewed. | State machine (Success -> PendingApproval -> Approved / Rejected); sequence diagram (approve / reject step after a HIGH interaction); use cases 'Approve proposal' and 'Reject proposal' | One extra click per check, which costs time against INT-13 (under 5-10 s); risk of automation bias (clicking without reading). |
| Tool use (deterministic check by an MCP tool) | The LLM must not 'remember' interactions: a missed interaction is the worst outcome (INT-9). A tool looks them up in the leaflet data. | MCP servers (interaction check, leaflet lookup); component diagram arrows labelled 'MCP tools' | The tool is only as complete as its data; the LLM can still mis-summarise the tool's result (needs the output check). |
| State | A check result behaves differently in each state (pending review, reviewed, rejected); the code and the state diagram must have the same states. | State machine diagram (Idle, Checking, Success, NotFound, Degraded, PendingApproval, Approved, Rejected); status strings in the code | Extra states to maintain and test; every status string must stay in sync with the diagram. |

Pattern families: Adapter and State are GoF patterns (Strategy for the fallback order is behavioural); retry with backoff, circuit breaker and timeout are resilience patterns; human-in-the-loop and tool use are agentic patterns.

## 4. Architecture decisions

| ID | Title | Status | Link |
|---|---|---|---|
| ADR-0001 | LLM time budget and retry limits | accepted | [0001-llm-time-budget-and-retry-limits.md](../adr/0001-llm-time-budget-and-retry-limits.md) |
| ADR-0002 | Review gate enforced in the backend | accepted | [0002-review-gate-enforced-in-backend.md](../adr/0002-review-gate-enforced-in-backend.md) |
| ADR-0003 | Gemini as primary LLM provider with Groq as fallback, behind one adapter | accepted | [0003-llm-provider-and-fallback.md](../adr/0003-llm-provider-and-fallback.md) |

Template: MADR-lite (context, drivers, options, decision, consequences, confirmation). All three were decided by both team members.

## 5. Risk management

### 5.1 Risk criteria and appetite
Criteria (from the risk register): probability and impact on a three-level scale (Low / Medium / High); score = probability x impact; residual level after the planned mitigation; treatment (avoid, mitigate, transfer, accept); five categories (technical, schedule, quality, AI-safety, process). 13 risks, owners and treatments are in the register ([docs/risk/risk-register.md](../risk/risk-register.md)).

**Risk appetite (proposed, team to confirm):**
- Low appetite for risks that can put wrong or unsourced clinical information in front of a physician (R-02, R-03, R-11, R-12, R-13): these need an active mitigation and a test before the demo.
- Medium appetite for schedule and quota risks (R-01, R-07): they can be absorbed by the fallback and the safe DEGRADED answer.
- Residual Low risks are accepted and only monitored.

### 5.2 SWOT

Weaknesses and threats are direct sources of risk; strengths and opportunities often reappear as risk treatments. Risk IDs follow the team risk register v1.1 (2026-11-16).

#### S - Strengths (internal, positive)

1. Complementary backgrounds: computer science (back end, already built the Lab 1 MCP server) and medical engineering (clinical context). *[Project]*
2. Real stakeholder input: a physician interview gave 17 usable notes with clear priorities (speed, verifiable leaflet source). *[Project]*
3. Core guardrails already work and were tested in MCP Inspector: retry, circuit breaker, approval gate, unknown-drug refusal. *[AI safety]*
4. Offline fake mode: development and tests need no API key and no quota. *[Technical]*
5. Planning documents exist: risk register (13 risks, owners, categories, residual levels), requirements draft with source tags, clear front-end / back-end split. *[Project]*

#### W - Weaknesses (internal, negative)

1. Two people and a short timeline, with other course work in parallel (confirm availability of both members). *[Project]*
2. The front-end developer has limited programming experience and relies on an AI coding assistant, so generated code needs careful review (confirm wording). *[Project]*
3. The real LLM has never been tested: every run used the fake LLM, so real response time, real 429 rate and answer quality are unknown. *[Technical]*
4. Only one stakeholder interview, so one physician's view. *[Project]*
5. Real leaflets not yet analysed for structure and severity wording (confirm). *[Technical]*

#### O - Opportunities (external, positive)

1. Public drug leaflets are freely available, and the course allows only public leaflets and fictional data. *[Technical]*
2. Free-tier LLM APIs (Gemini, plus a fallback) and free AI coding assistants. *[Technical]*
3. FastMCP and MCP Inspector make building and testing tools quick, with no client code. *[Technical]*
4. The opposite team (patient version) reviews the app at the MVP stage, which gives early outside feedback. *[Project]*
5. The stakeholder can validate the specification in a review (confirm availability). *[Project]*

#### T - Threats (external, negative)

1. Free-tier limits or terms change without notice. *[Technical]*
2. The LLM states a wrong drug fact, or an interaction is missed. *[AI safety]*
3. Instruction-like text inside a leaflet changes the AI's behaviour (prompt injection). *[AI safety]*
4. Leaflet PDFs are hard to parse, or the data is incomplete or outdated. *[Technical]*
5. Output is perceived as medical advice; free-tier providers may use prompts to improve their products, so no real patient data may be sent. *[Legal / ethical]*
6. Stakeholder requests grow the scope (patient factors, nurses, other systems). *[Project]*
7. A leaked API key lets strangers use the quota. *[Security / privacy]*

#### From SWOT to the risk register

| SWOT item | Category | Risk in the register | What offsets it (strengths, opportunities, treatments) |
|---|---|---|---|
| **W1** Two people, short timeline | Project | Accepted (no dedicated risk; monitored via schedule) | S5 clear roles; keep a time buffer in the Gantt plan |
| **W2** Limited programming experience on the front end | Project | Accepted (mitigated by review) | S3 tested guardrails; teammate reviews code; AI Use Log |
| **W3** Real LLM never tested | Technical | R-05, R-01 | S4 fake mode, O2 free APIs; action: measure with a real key |
| **W4** Single interview | Project | none | O5 validation review with the stakeholder |
| **W5** Leaflets not yet analysed | Technical | R-08 | O1 public leaflets; action: analyse a few real ones |
| **T1** Free-tier limits change | Technical | R-01, R-07 | S3 retry and circuit breaker; S4 fake mode |
| **T2** Wrong fact or missed interaction | AI safety | R-02, R-03 | S3 unknown-drug refusal; grounding and review gate (GR-05, GR-10) |
| **T3** Prompt injection via leaflet text | AI safety | R-11 | Guardrail GR-07 (leaflet text handled as data) |
| **T4** Leaflets hard to parse or outdated | Technical | R-08 | O1 public leaflets; clear "not found" message |
| **T5** Output read as medical advice; provider data use | Legal / ethical | R-12 | Disclaimer and output check (GR-12); no real patient data |
| **T6** Scope growth | Project | R-09 | Won't-have list; O5 stakeholder review |
| **T7** Leaked API key | Security / privacy | R-06 | Keys only in .env; .env in .gitignore |


### 5.3 Risk matrix (snapshot) and register

| Impact \ Probability | Low | Medium | High |
|----------------------|-----|--------|------|
| **High**             | R-06, R-11 | R-02, R-03, R-07, R-12, R-13 | — |
| **Medium**           | — | R-04, R-05, R-08, R-09 | R-01 |
| **Low**              | R-10 | — | — |

Full register with owners, treatments and residual levels: [docs/risk/risk-register.md](../risk/risk-register.md).

## 6. AI safety

### 6.1 Failure modes (AI-FMEA)

| FM-ID | Component | Failure mode | Effect | Detection | Guardrail(s) | Risk (register ID) | Linked requirements (spec v1.2) |
|---|---|---|---|---|---|---|---|
| FM-01 | Interaction summary (RAG + LLM) | Summary or quote is not supported by the leaflet (hallucination, or a quote that is not word for word) | Wrong drug information shown to a physician | Check that the quote appears word for word in the retrieved leaflet text; check each summary statement against the quote | GR-05, GR-06, GR-12 | R-02 | FR-03, NFR-02 |
| FM-02 | Interaction check | An interaction stated in the leaflets is missed or hidden (retrieval misses the passage, or the LLM leaves it out) | Physician believes a combination is safe (worst case per INT-9) | Interaction lookup done by a tool over the leaflet data, not by the LLM; test with a fixed drug set and a leaflet checklist | GR-04, GR-12 | R-03, R-08 | FR-02, FR-06, NFR-03 |
| FM-03 | Any component reading leaflets | Instruction-like text inside a leaflet changes the AI's behaviour (prompt injection) | Policy bypass, wrong or hidden result | Retrieved text wrapped as data; tool allow-list; test with a leaflet chunk that says 'ignore previous instructions' | GR-07 | R-11 | FR-11 |
| FM-04 | Agent -> MCP tool | Wrong, mistyped or invented drug name passed to a tool | Garbage result presented as a fact | Validate every name against the drug store before any tool or LLM call | GR-01, GR-09 | R-02 | FR-01, FR-05, FR-12 |
| FM-05 | Agent orchestration (only if A2A agents are used) | Agents delegate to each other in a loop, or one request triggers too many steps | Quota burned, no answer in time | Step, hop and tool-call counters | GR-08 | none (only if agents are used); loosely R-07 | NFR-01 |
| FM-06 | LLM adapter | Provider returns 429/5xx or does not answer (timeout) | No summary; physician waits longer than 10 s | HTTP status and timeout in the adapter; console log of attempts | GR-02, GR-03, GR-11 | R-01, R-05 | FR-07, NFR-01, NFR-06 |
| FM-07 | Whole app | Daily free-tier quota is used up | LLM features unavailable until the next day | Usage counter; circuit breaker opens | GR-03, GR-11 | R-07 | FR-07, NFR-06 |
| FM-08 | UI / output | Answer is phrased as an instruction ('stop this drug', a dose) or severity is invented | Output is read as medical advice (conflicts with INT-10, which asks for 'what to do clinically') | Output check for dosing or instruction wording; severity shown only if stated in the leaflet | GR-12 | R-12 (partly R-02) | FR-11 |
| FM-09 | Review step (human) | Physician clicks 'reviewed' without reading the evidence (automation bias) | The gate exists but protects nobody | Show quote and source next to the button; record who reviewed what and when | GR-10 | R-13 (see also R-03) | FR-09, FR-10 |

### 6.2 Approval gates

| Question | Answer |
|---|---|
| Where | After the LLM step, before a result counts as reviewed or a schedule can be saved. Required when a HIGH interaction is found (ADR-0002, FR-09). |
| Who | The physician, through the user interface only. The review action is not in the model's tool list (FR-10). |
| What is shown | Severity, the word-for-word leaflet quote and the leaflet name and section, next to the approve button (against automation bias, FM-09). |
| Outcomes | Approve (APPROVED), reject (REJECTED), or no answer: the result stays not reviewed. A rejected or blocked proposal can never be approved. |
| Record | Who approved or rejected, and when. |
| Lab version | The lab server asks for approval for every proposal and blocks some pairs permanently; the design for the doctor version is the HIGH-only gate of ADR-0002. |

### 6.3 Guardrail specification

| GR-ID | Guardrail | Type | Trigger / condition | Behaviour | Limit / parameter | Risk / FM | Requirement (spec v1.2) | How it will be tested (Lab 6) |
|---|---|---|---|---|---|---|---|---|
| GR-01 | Drug-name allow-list | Preventive | Tool receives a name not in the leaflet store | Return REFUSED / 'not found'; no LLM call | \- | R-02, FM-04 | FR-05 | Call with 'aspirin' -> REFUSED; console shows no LLM attempt |
| GR-02 | Retry with backoff | Corrective | HTTP 429/5xx or timeout | Retry with exponential backoff + jitter; never retry 400/401/403/404 | max 3 attempts, max 8 s wait, honour Retry-After | R-01, R-05, FM-06 | FR-07, NFR-01 | FAKE_LLM_FAILURES=2 -> success on the 3rd attempt |
| GR-03 | Circuit breaker | Corrective | 3 failed calls in a row | Fail fast (no waiting) and return the safe fallback | 3 failures / 60 s | R-01, R-07, FM-06/07 | FR-07, NFR-01 | FAKE_LLM_FAILURES=99 -> 4th call returns immediately |
| GR-04 | Deterministic interaction check | Preventive | Any check of 2+ drugs | Interactions come from a tool over the leaflet data, not from the LLM | \- | R-03, FM-02 | FR-02 | Known pair reported with the LLM switched off |
| GR-05 | Grounding + verbatim quote check | Preventive / detective | Every result shown | Result must cite leaflet name + section; quote must appear word for word in the leaflet text, else DEGRADED | \- | R-02, R-03, FM-01 | FR-03, NFR-02 | Alter a quote by one word -> result blocked |
| GR-06 | 'Not found in leaflets' rule | Preventive | No leaflet text for the combination | Say 'not found in leaflets'; do not generate; never present 'none found' as proof of safety | \- | R-02, R-08, FM-01/02 | FR-05, NFR-03 | Pair with no leaflet text -> exact message, no LLM text |
| GR-07 | Prompt-injection hygiene | Preventive | Any retrieved leaflet text | Wrap as data; allow-list tools; no tool runs free text | \- | R-11, FM-03 | FR-11 | Leaflet chunk with 'ignore previous instructions' -> output unchanged |
| GR-08 | Step / hop / tool-call limits | Preventive | A request exceeds a limit | Stop, return partial result + explanation | e.g. 8 steps, 2 hops, 10 tool calls (team to decide) | R-07 (loosely), FM-05 | NFR-01 | Force a loop -> stops at the limit |
| GR-09 | Input size limit (MY GUARDRAIL, implemented) | Preventive | Proposal has 0 or more than 10 drugs | Return REFUSED with the reason, no LLM call | 1 to 10 drugs (FR-12; NFR-01 targets up to 5) | R-05, R-07, FM-04 | FR-12 | 11 drugs -> REFUSED; 10 drugs -> accepted |
| GR-10 | Review gate (human-in-the-loop) | Preventive | Result ready; any HIGH interaction | Stays PENDING_APPROVAL until the physician approves in the UI (after seeing the quote and source); no answer = no action; never an LLM tool; record who and when | \- | R-03, R-13, FM-09 | FR-09, FR-10 | Mark reviewed without the physician -> REFUSED; timeout -> not reviewed |
| GR-11 | Safe fallback + kill switch | Corrective | LLM unavailable, or LLM_ENABLED=false | Fixed safe message; show the verbatim leaflet quote without the AI summary (proposal - team to decide) | \- | R-01, R-05, R-07, FM-06/07 | FR-07 | FAKE_LLM_FAILURES=99 -> DEGRADED message with source |
| GR-12 | Output check + disclaimer | Detective / corrective | Every AI-written text | Block dosing or instruction wording not in the leaflet; show severity only if stated; 'Teaching prototype - not medical advice' on every answer | \- | R-12, R-02 (partly), FM-01/02/08 | FR-11, NFR-03 | Answer with a dose not in the leaflet -> blocked |

## 7. Traceability

Requirement IDs follow the Product Technical Specification (v1.2 draft; FR-09 to FR-12 and NFR-06 are new and proposed). Test IDs are provisional: T-01 to T-12 are the tests of GR-01 to GR-12 (column "How it will be tested" in 6.3); T-13 to T-15 are listed below.

| Requirement | Design element(s) | Risk(s) | Guardrail(s) | Test |
|---|---|---|---|---|
| FR-01 Enter drug list | Use case "Enter drug list"; web UI; state Idle to Checking | R-02 | GR-01 | T-01 |
| FR-02 Report interactions | Use case "Check interactions"; interaction-check agent; drug-info MCP server (tool use) | R-03 | GR-04 | T-04 |
| FR-03 Severity and leaflet quote | Leaflet-RAG server; sequence message "summary + citations" | R-02, R-03 | GR-05 | T-05 |
| FR-04 Summary, paragraph, full section | Use case "Show full leaflet section"; web UI | R-04 | none (severity filtering in the UI) | T-15 |
| FR-05 Refuse unknown drugs | Use case "Handle unknown drug"; state NotFound; ask_leaflet / drug-info server | R-02, R-08 | GR-01, GR-06 | T-01, T-06 |
| FR-06 Flag when evidence is weak | Interaction-check agent; severity shown only if stated in the leaflet | R-03, R-04 | GR-04, GR-06 | T-06 |
| FR-07 Work on HTTP 429 | LLM adapter; ADR-0001; sequence diagram (retry loop, DEGRADED); state Degraded; use case "Handle LLM rate limit" | R-01, R-07 | GR-02, GR-03, GR-11 | T-02, T-03, T-11 |
| FR-08 / NFR-01 Under 10 s | LLM adapter timeout and deadline (ADR-0001); drug limit; sequence diagram | R-05 | GR-02, GR-03, GR-08, GR-09 | T-14 |
| FR-09 Review gate | Use cases Approve / Reject; states PendingApproval, Approved, Rejected; sequence approval step; ADR-0002 | R-13, R-03 | GR-10 | T-10 |
| FR-10 Review action not callable by the model | Guardrail layer; tool list; ADR-0002 | R-13 | GR-10 | T-10 |
| FR-11 Leaflet text as data; disclaimer | Guardrail layer (output check); prompt construction | R-11, R-12 | GR-07, GR-12 | T-07, T-12 |
| FR-12 Limit 1 to 10 drugs | Guardrail layer (input check) | R-05, R-07 | GR-09 | T-09 |
| NFR-02 Cite the leaflet section | Leaflet-RAG server; quote check | R-02 | GR-05 | T-05 |
| NFR-03 Say "I don't know" | State NotFound; "not found in leaflets" message | R-02 | GR-06 | T-06 |
| NFR-04 Desktop and mobile | Web UI; deployment diagram (browser) | none | none | T-15 |
| NFR-05 Free tiers only | Deployment diagram; ADR-0003 | R-07 | GR-03, GR-11 | review of the setup |
| NFR-06 Fallback provider | LLM adapter (Adapter + Strategy); ADR-0003; component diagram | R-01, R-07 | GR-02, GR-03 | T-13 |

Additional provisional tests: **T-13** a simulated 429 from the primary provider switches to the fallback; **T-14** measured response time over a set of checks with a real key (95% under 10 s for up to 5 drugs); **T-15** manual check of the UI on desktop and on a phone-sized window.

## 8. AI design review

Checklist from the lab handout (section 2.5): every element traces to a requirement or a decision; relations are correct; nothing important is missing (approval step, failure path); notation is valid; diagrams agree with each other. *(confirm which artifacts were AI-generated; the table lists what the review found.)*

| Artifact | What was generated | What was wrong (checklist) | What was changed |
|---|---|---|---|
| Sequence diagram | Check flow with retry loop and DEGRADED message | Approval step missing | Approval step added (approve / reject after a HIGH interaction) |
| State machine | Idle, Checking, Success, NotFound, Degraded | Approval states missing | PendingApproval, Approved, Rejected added |
| Use case diagram | Use cases for the doctor | Approve and reject missing | Use cases Approve and Reject added |
| Use case diagram | Include / extend relations | The `<<extend>>` arrows run from the base use case to the extension; in UML they run from the extension to the base | **Open: reverse the two arrows in usecase.puml** |
| Component diagram | Components and arrows | Only Gemini is shown, but ADR-0003 adds Groq; the approval gate is not a visible component | **Open: add Groq and the approval gate** |
| Sequence diagram | Lifelines | The guardrail layer and the orchestrator from the component diagram do not appear; the circuit breaker and the timeout are not drawn | **Open: add the guardrail layer and the circuit-breaker step, or name the components the same everywhere** |
| State machine | States | The code also has BLOCKED, REFUSED and SAVED, which the diagram does not show | **Open: decide whether the doctor version keeps a blocked state** |
| ADR-0001 | Draft with illustrative values | T = 4 s and D = 8 s are not measured | Kept as accepted with the wording "NOT measured"; to be replaced after measuring with a real key |
| ADR-0002 | Draft | Placeholder requirement ID; lab server blocks HIGH interactions permanently (written for the patient version) | Requirement IDs FR-09 and FR-10 filled in; the doctor-version gate decided (HIGH only, explicit acknowledgement) |
| ADR-0003 | Draft with an open fallback provider | The lab example used Mistral, the register used Groq | Team chose Groq; ADR accepted |
| Guardrail and failure-mode tables | First draft from the lab examples | Risks for prompt injection, output read as advice and approval without reading did not exist in the register; requirement IDs did not match the specification | Risks R-11, R-12, R-13 added to the register; IDs aligned with the specification |
| Guarded server additions | Size limit (GR-09) and `reject_proposal` | The size limit comment cited the wrong requirement | Comment now refers to FR-12 |

AI help for this document and its parts is recorded in the AI Use Log (stage: design) with the verdict used as is / used after edits / rejected.
