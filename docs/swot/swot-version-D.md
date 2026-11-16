# SWOT - Version D (physician)

Weaknesses and threats are direct sources of risk; strengths and opportunities often reappear as risk treatments. Risk IDs follow the team risk register v1.1 (2026-11-16).

## S - Strengths (internal, positive)

1. Complementary backgrounds: computer science (back end, already built the Lab 1 MCP server) and medical engineering (clinical context). *[Project]*
2. Real stakeholder input: a physician interview gave 17 usable notes with clear priorities (speed, verifiable leaflet source). *[Project]*
3. Core guardrails already work and were tested in MCP Inspector: retry, circuit breaker, approval gate, unknown-drug refusal. *[AI safety]*
4. Offline fake mode: development and tests need no API key and no quota. *[Technical]*
5. Planning documents exist: risk register (13 risks, owners, categories, residual levels), requirements draft with source tags, clear front-end / back-end split. *[Project]*

## W - Weaknesses (internal, negative)

1. Two people and a short timeline, with other course work in parallel (confirm availability of both members). *[Project]*
2. The front-end developer has limited programming experience and relies on an AI coding assistant, so generated code needs careful review (confirm wording). *[Project]*
3. The real LLM has never been tested: every run used the fake LLM, so real response time, real 429 rate and answer quality are unknown. *[Technical]*
4. Only one stakeholder interview, so one physician's view. *[Project]*
5. Real leaflets not yet analysed for structure and severity wording (confirm). *[Technical]*

## O - Opportunities (external, positive)

1. Public drug leaflets are freely available, and the course allows only public leaflets and fictional data. *[Technical]*
2. Free-tier LLM APIs (Gemini, plus a fallback) and free AI coding assistants. *[Technical]*
3. FastMCP and MCP Inspector make building and testing tools quick, with no client code. *[Technical]*
4. The opposite team (patient version) reviews the app at the MVP stage, which gives early outside feedback. *[Project]*
5. The stakeholder can validate the specification in a review (confirm availability). *[Project]*

## T - Threats (external, negative)

1. Free-tier limits or terms change without notice. *[Technical]*
2. The LLM states a wrong drug fact, or an interaction is missed. *[AI safety]*
3. Instruction-like text inside a leaflet changes the AI's behaviour (prompt injection). *[AI safety]*
4. Leaflet PDFs are hard to parse, or the data is incomplete or outdated. *[Technical]*
5. Output is perceived as medical advice; free-tier providers may use prompts to improve their products, so no real patient data may be sent. *[Legal / ethical]*
6. Stakeholder requests grow the scope (patient factors, nurses, other systems). *[Project]*
7. A leaked API key lets strangers use the quota. *[Security / privacy]*

## From SWOT to the risk register

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
