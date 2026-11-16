# ADR-0003: Use Gemini as primary LLM provider with Groq as fallback, behind a single adapter

- Status: accepted
- Date: 2026-11-16
- Deciders: VV, MD
- Related: R-01, R-07, GR-02, GR-03, NFR-01; constraint: free tiers only (course handout); see also ADR-0001

## Context and problem
The application calls an LLM for summaries. We may use only free tiers, which have per-minute and per-day limits.
The risk register lists the rate limit (R-01) and quota exhaustion (R-07) as risks, and names Gemini and Groq as the two providers used in development.
The lab's example uses Gemini as the main provider and Mistral as the fallback. Our team used Gemini and Groq.
How do we keep the application usable when the main provider is throttled or down?

## Decision drivers
- Graceful degradation on HTTP 429 (R-01, FR-07).
- No paid services.
- Maintainability: the rest of the app should not depend on one vendor's API.
- Consistency with the providers already used and recorded in the risk register.

## Considered options
1. Gemini only, called directly from the code that needs it.
2. Gemini as primary plus Groq as fallback, behind one adapter (Adapter + Strategy).
3. A local open-weight model.

## Decision
Chosen option 2: Gemini primary, Groq fallback, behind a single adapter.
This addresses R-01 and R-07 within the free-tier constraint and without new hardware. The adapter is the one place for retries, timeouts and the circuit breaker (ADR-0001).

## Consequences
- Good: one place for retries, timeouts and the circuit breaker; switching models is a configuration change.
- Good: matches the providers already used in development and listed in the risk register.
- Bad: two providers to configure and test; answers differ slightly between models, so tests must not depend on exact wording.
- Bad: the lab server only has Gemini and a fake mode, so the Groq path still has to be implemented.

## Confirmation
A simulated 429 from the primary provider switches the answer to the fallback; checked in the Lab 6 tests.
