# Guarded MCP Server Exercises – Results (Version D, Lab 3)

**Author:** MD  
**Date:** 2026-11-16  
**Environment:** MCP Inspector (`LLM_PROVIDER=fake`)  
**Related:** `guarded_server.py`, AI Use Log (Exercise 6)

## Summary

| Exercise | Result | Guardrail | Test input / steps | Evidence | Verdict |
|----------|--------|-----------|--------------------|----------|---------|
| 1 Retry | 2 failures (HTTP 429), success on the 3rd attempt; about 3-4 s; status OK | Retry with backoff (GR-02) | `FAKE_LLM_FAILURES=2`; `ask_leaflet(warfarin, monitoring?)` | Page 2 | As expected |
| 2 Give up safely | Calls 1-3 each made 3 attempts (about 3-4 s) and returned DEGRADED; circuit OPEN for 60 s logged on call 3; calls 4 and 5 instant (about 30 ms), 'circuit open' | Circuit breaker (GR-03) | `FAKE_LLM_FAILURES=99`; `ask_leaflet` 5 times | Page 3 | As expected |
| 3 Input check | aspirin → REFUSED (not in leaflet store), 36 ms; LLM not called (no new console lines) | Drug-name allow-list (GR-01) | `ask_leaflet(aspirin, monitoring?)` | Page 4-5 | As expected |
| 4 Approval gate | Propose → PENDING_APPROVAL; save before approval → REFUSED; approve → APPROVED (approved_by set); save → SAVED | Approval gate (GR-10) | `propose_schedule([warfarin, paracetamol])`; save; approve; save | Page 6-9 | As expected |
| 5 Blocked | propose [warfarin, ibuprofen] → BLOCKED with the pair listed; approve → REFUSED 'proposal is BLOCKED'; save → REFUSED; reject → REFUSED 'proposal is BLOCKED' | Approval gate (GR-10) | `propose_schedule([warfarin, ibuprofen])`; approve; save; reject | Page 10-14 | As expected |
| 6 My guardrail | 11 drugs → REFUSED 'got 11'; [] → REFUSED 'got 0'; [paracetamol] → PENDING_APPROVAL; reject → REJECTED (rejected_by set); approve after reject → REFUSED 'proposal is REJECTED' | Input size limit (GR-09) + reject_proposal | propose with 11 and 0 drugs; propose [paracetamol]; reject; approve | Page 15-18 | As expected |

## Notes
- Exercise 6 uses the two additions to `guarded_server.py` (size limit GR-09 and `reject_proposal`). They were written with AI help and are logged in the AI Use Log.
- All exercises behaved as expected under the fake LLM provider.
- Full evidence screenshots are in the original PDF (pages 2–18).
