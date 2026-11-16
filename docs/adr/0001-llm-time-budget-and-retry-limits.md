# ADR-0001: Give the LLM step an overall time budget, a shorter timeout and a safe fallback

- Status: accepted
- Date: 2026-11-16
- Deciders: VV, MD
- Related: NFR-01 (response time), FR-07 (DEGRADED message), R-01, R-05, R-07, GR-02, GR-03, GR-11; interview INT-1 (answers 13 and 16)

## Context and problem
The physician said a check must take under 5-10 seconds (INT-1, answer 13) and that the tool is not useful if it is slower (INT-1, answer 16).
The lab's guarded call uses 3 attempts, waits of about 1 s and 2 s, and a 30 s timeout per request, with no overall limit.
In the offline test with fake failures, falling back to the safe message took about 3-4 s. If the real service does not answer at all, 3 attempts x 30 s plus the waits is roughly 93 s.
Which limits should the LLM call use so that the physician never waits longer than the agreed time, and who owns the numbers?

## Decision drivers
- NFR-01: the result is displayed within 10 s (INT-1, answers 13 and 16).
- R-01 and R-07: free-tier rate limits and daily quota, so retries must not waste quota.
- Safety: if the LLM step fails, show the safe fallback and never guess (GR-11).
- Consistency: the same numbers in the specification, the sequence diagram and the code.

## Considered options
1. Keep the lab defaults (3 attempts, 30 s timeout, no overall limit).
2. A shorter timeout per attempt plus one overall deadline for the LLM step; stop retrying when the next attempt would pass the deadline, then show the safe fallback.
3. No retries: the first failure goes straight to the fallback.

## Decision
Chosen option 2, because it is the only option that keeps the 10 s limit in the worst case and still absorbs a brief rate-limit error (R-01).
Values: per-attempt timeout T and overall LLM deadline D, with D below 10 s. Illustrative starting point, NOT measured: T = 4 s, D = 8 s. Set the real values after measuring response times with a real key.
Owner of the numbers: the back-end developer. The same values must appear in the specification, the sequence diagram and the code.

## Consequences
- Good: the worst-case wait is bounded; matches the register's mitigation for R-05 (timeout and DEGRADED path).
- Bad: a slow but valid answer can be cut off; one more setting to tune; real response times are unknown until measured.
- Bad: the lab server must be changed (it has a 30 s timeout and no overall deadline).
- Related idea, for a separate ADR: show the interaction and the leaflet quote first and the AI summary afterwards, so the 10 s applies to what the physician needs most.

## Confirmation
- With FAKE_LLM_FAILURES=99 the total time until the DEGRADED answer is at most D.
- A simulated slow response (needs a small addition to the fake mode) is cut off after T.
- Measured real response times are recorded in the repository.
- Check that the numbers are identical in the specification, the diagram and the code.
