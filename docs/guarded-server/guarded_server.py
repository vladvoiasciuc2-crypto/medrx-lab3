"""Lab 3 - guardrails around an LLM call and an approval gate (toy data, NOT medical advice)."""
import logging
import os
import random
import sys
import time
import uuid

import requests
from fastmcp import FastMCP

# stdio transport: stdout belongs to the protocol, so we log to stderr (Inspector -> Console tab).
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("guarded")

mcp = FastMCP("pillbox-guarded")

# ---- Toy data (same as Lab 1) -------------------------------------------------------
DRUGS = {
    "ibuprofen": {"class": "NSAID", "notes": "Take with food."},
    "warfarin": {"class": "anticoagulant", "notes": "Needs INR monitoring."},
    "paracetamol": {"class": "analgesic", "notes": "Avoid alcohol."},
}
INTERACTIONS = {frozenset({"ibuprofen", "warfarin"}): "HIGH"}

# ---- Guardrail limits: each one should appear in your risk register / guardrail spec ----
MAX_ATTEMPTS = 3          # retry limit: 1 call + 2 retries, then give up
BASE_DELAY_S = 1.0        # exponential backoff: 1 s, 2 s, 4 s ... (+ jitter)
MAX_DELAY_S = 8.0         # never wait longer than this between attempts
TIMEOUT_S = 30            # per-request timeout
CB_THRESHOLD = 3          # circuit breaker opens after 3 failed calls in a row
CB_COOLDOWN_S = 60        # ... and stays open for 60 s
MAX_DRUGS_PER_PROPOSAL = 10   # MY GUARDRAIL (GR-09): input size limit, FR-12: hard limit of 10 drugs (NFR-01 targets up to 5)
RETRYABLE = {429, 500, 502, 503, 504}
SAFE_FALLBACK = ("The assistant is temporarily unavailable. Please read the leaflet section "
                 "directly or ask a pharmacist. (Teaching prototype - not medical advice.)")


class LLMUnavailable(Exception):
    """Raised when the guarded call gives up (retry limit reached or circuit open)."""


class CircuitBreaker:
    def __init__(self, threshold: int, cooldown_s: float):
        self.threshold, self.cooldown_s = threshold, cooldown_s
        self.failures, self.opened_at = 0, None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True                                     # CLOSED
        if time.monotonic() - self.opened_at >= self.cooldown_s:
            return True                                     # HALF-OPEN: let one call try
        return False                                        # OPEN

    def success(self) -> None:
        self.failures, self.opened_at = 0, None

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = time.monotonic()
            log.warning("circuit OPEN for %ss", self.cooldown_s)


breaker = CircuitBreaker(CB_THRESHOLD, CB_COOLDOWN_S)
_fake_failures_left = int(os.environ.get("FAKE_LLM_FAILURES", "0"))  # for the exercises


def _raw_gemini(prompt: str) -> requests.Response:
    global _fake_failures_left
    if os.environ.get("LLM_PROVIDER") == "fake":            # offline mode, no API key needed
        resp = requests.Response()
        if _fake_failures_left > 0:
            _fake_failures_left -= 1
            resp.status_code = 429
        else:
            resp.status_code = 200
            resp._content = (b'{"candidates":[{"content":{"parts":[{"text":'
                             b'"(fake LLM) Answer based on the leaflet."}]}}]}')
        return resp
    model = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    return requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=TIMEOUT_S,
    )


def guarded_llm_call(prompt: str) -> str:
    """Retry with exponential backoff + jitter, a hard attempt limit and a circuit breaker."""
    if not breaker.allow():
        raise LLMUnavailable("circuit open")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            r = _raw_gemini(prompt)
        except requests.RequestException as e:              # timeout, DNS, connection reset
            status, retry_after = None, None
            log.warning("attempt %d: network error %s", attempt, type(e).__name__)
        else:
            if r.status_code == 200:
                breaker.success()
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            status, retry_after = r.status_code, r.headers.get("Retry-After")
            log.warning("attempt %d: HTTP %s", attempt, status)
            if status not in RETRYABLE:                     # 400/401/403/404: retrying won't help
                break
        if attempt < MAX_ATTEMPTS:
            delay = min(MAX_DELAY_S, BASE_DELAY_S * 2 ** (attempt - 1)) + random.uniform(0, 0.5)
            if retry_after and retry_after.isdigit():
                delay = min(MAX_DELAY_S, float(retry_after))
            time.sleep(delay)
    breaker.failure()
    raise LLMUnavailable(f"gave up after {attempt} attempt(s)")


@mcp.tool
def ask_leaflet(drug: str, question: str) -> dict:
    """Answer a question about ONE known drug, using only its leaflet text (toy dataset)."""
    name = drug.strip().lower()
    if name not in DRUGS:                                   # input guardrail: no unknown drugs
        return {"status": "REFUSED", "reason": f"'{drug}' is not in the leaflet store."}
    leaflet = f"{name}: {DRUGS[name]['class']}. {DRUGS[name]['notes']}"
    prompt = (f"Answer ONLY from this leaflet text. If the answer is not there, say "
              f"'not found in leaflet'.\nLeaflet: {leaflet}\nQuestion: {question[:500]}")
    try:
        answer = guarded_llm_call(prompt)
    except LLMUnavailable as e:                             # failure mode -> safe degradation
        log.error("LLM unavailable: %s", e)
        return {"status": "DEGRADED", "answer": SAFE_FALLBACK}
    return {"status": "OK", "answer": answer, "source": f"drug://{name}/leaflet",
            "disclaimer": "Teaching prototype - not medical advice."}


# ---- Approval gate: the AI may PROPOSE, only a human may APPROVE --------------------------
PROPOSALS: dict[str, dict] = {}


@mcp.tool
def propose_schedule(drugs: list[str]) -> dict:
    """Create a schedule proposal. Nothing is saved until a human approves it."""
    if len(drugs) == 0 or len(drugs) > MAX_DRUGS_PER_PROPOSAL:      # GR-09: input size limit
        return {"status": "REFUSED",
                "reason": f"a proposal needs 1 to {MAX_DRUGS_PER_PROPOSAL} drugs, got {len(drugs)}"}
    names = [d.strip().lower() for d in drugs]
    unknown = [n for n in names if n not in DRUGS]
    if unknown:
        return {"status": "REFUSED", "reason": f"unknown drug(s): {unknown}"}
    high = [sorted(pair) for pair, level in INTERACTIONS.items()
            if level == "HIGH" and pair <= set(names)]
    pid = uuid.uuid4().hex[:8]
    PROPOSALS[pid] = {"drugs": names, "status": "BLOCKED" if high else "PENDING_APPROVAL",
                      "high_interactions": high}
    return {"proposal_id": pid, **PROPOSALS[pid]}


@mcp.tool
def approve_proposal(proposal_id: str, approver: str) -> dict:
    """HUMAN step (in the UI, not called by the model): approve a pending proposal."""
    p = PROPOSALS.get(proposal_id)
    if p is None:
        return {"status": "REFUSED", "reason": "no such proposal"}
    if p["status"] != "PENDING_APPROVAL":                   # BLOCKED can never be approved
        return {"status": "REFUSED", "reason": f"proposal is {p['status']}"}
    p.update(status="APPROVED", approved_by=approver)
    return {"proposal_id": proposal_id, **p}


@mcp.tool
def reject_proposal(proposal_id: str, approver: str) -> dict:
    """HUMAN step (in the UI, not called by the model): reject a pending proposal."""
    p = PROPOSALS.get(proposal_id)
    if p is None:
        return {"status": "REFUSED", "reason": "no such proposal"}
    if p["status"] != "PENDING_APPROVAL":                   # only a pending proposal can be rejected
        return {"status": "REFUSED", "reason": f"proposal is {p['status']}"}
    p.update(status="REJECTED", rejected_by=approver)
    return {"proposal_id": proposal_id, **p}


@mcp.tool
def save_schedule(proposal_id: str) -> dict:
    """Persist a schedule - allowed ONLY after approval."""
    p = PROPOSALS.get(proposal_id)
    if p is None or p["status"] != "APPROVED":
        return {"status": "REFUSED", "reason": "approval required before saving"}
    p["status"] = "SAVED"
    return {"proposal_id": proposal_id, **p}


if __name__ == "__main__":
    mcp.run()  # stdio by default
