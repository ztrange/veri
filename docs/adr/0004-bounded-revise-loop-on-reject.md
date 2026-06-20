# Bounded revise loop on a REJECT verdict

When a blind verifier returns `REJECT`, the conductor spawns a **fresh** developer leaf
given the issue spec, the current test/code, and the rejection reason, then re-verifies.
This repeats up to a small attempt budget (default **2**). If the verdict is still
`REJECT` after the budget is spent, the conductor bails the issue and escalates to the
human — it does not loop forever.

## Context

This is a distinct retry axis from the supervisor's: the supervisor retries a leaf that
went **silent/stuck** (no verdict); this revise loop handles a leaf that **finished with
a negative verdict**. Unbounded revision risks burning tokens forever on a pathological
case; immediate escalation isn't autonomous. A small cap is the balance — it mirrors the
reference suite's "one retry per item," here on the verdict axis.

## Consequences

Each revise attempt is a fresh leaf (claude -p leaves don't persist context), so the
rejection reason must be passed explicitly as the carry-forward signal. On final bail the
issue is escalated *with its trail* (see ADR-0005) so the human picks up where the loop
left off. The budget is a tunable constant, not a structural commitment.
