<!-- DRAFT written with AI help. Status stays "proposed" until BOTH team members agree. Delete this note when accepted. -->

# ADR-0002: Enforce the physician's review gate in the backend; a HIGH interaction needs an explicit acknowledgement

- Status: proposed
- Date: 2026-11-16
- Deciders: <initials of both members>
- Related: R-03, GR-10, FM-09, FR-xx (new requirement for spec v1.1); interview notes INT-7, INT-9, INT-11

## Context and problem
The physician is legally accountable for a prescription (INT-7) and a missed interaction is the worst outcome (INT-9).
The Lab 3 handout says that in the doctor version the gate comes before a check is marked "reviewed" and whenever a HIGH interaction is found, with an explicit "I have reviewed this", and that the model must never be able to open the gate.
The lab's example server blocks a HIGH interaction permanently, which was written for the patient version.
Where is the gate enforced, and what happens with a HIGH interaction?

## Decision drivers
- Legal responsibility stays with the physician (INT-7).
- The model must not be able to approve its own output.
- Show the evidence next to the button, because a person who approves without seeing the sources is not a real gate (automation bias, FM-09).
- No answer means no action: a timeout never leads to "reviewed".
- Speed: an extra click costs time (INT-13).

## Considered options
1. Gate in the user interface only; the backend accepts any caller.
2. Gate enforced in the backend as a state machine (pending review, reviewed, rejected); the review action is not in the model's tool list; a HIGH interaction can only be reviewed after an explicit acknowledgement with the quote and source shown; who and when are recorded.
3. Hard block on any HIGH interaction, as in the lab's patient-version example.

## Decision
Chosen option 2 (proposed), because option 1 can be bypassed by anything that calls the backend, including the model's tools, and option 3 takes the decision away from the physician, while the handout asks for an explicit review in the doctor version.

## Consequences
- Good: the model cannot approve; there is a record of who reviewed what and when; matches the handout's rules for the doctor version.
- Bad: one extra click per check, against INT-13.
- Bad: the physician may click without reading (FM-09); mitigated by showing the quote and source beside the button.
- Bad: the lab server must be changed, since it only has a permanent BLOCKED state for HIGH interactions.

## Confirmation
- Marking a check as reviewed without an approver returns REFUSED (as in Exercise 4).
- The review action is not in the model's tool list (checked in the tool listing).
- A HIGH interaction can only be reviewed after the acknowledgement step.
- If nobody responds, the check stays not reviewed.
