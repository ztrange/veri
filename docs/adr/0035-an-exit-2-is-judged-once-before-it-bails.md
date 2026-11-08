# An exit 2 is judged once before it bails

When a script exits 2 at an eligible site, the conductor launches an `adjudicate` leaf before
bailing. The leaf runs on opus by default, through `supervise.sh`. It answers RETRY, ROUTE (to a
route the procedure already defines at that site) or BAIL. Its budget is an axis of its own,
`VERI_ADJUDICATE_BUDGET`, adjudications per run with a default of 2. The exit-code API is
unchanged.

## Context

Measured on 2026-11-08 at `7627c54d59`, over 1354 committed metrics reports: 53 runs bailed, and
24 of those bails were sourced from an exit 2. `ci-timeout` alone accounts for 15. Each exit-2
site handles its own failure in its own prose, so a situation nobody anticipated bails the run,
and the fix has been to add one more special case per incident.

## Decision

- **A judgment, not a repair.** The leaf writes no file and no ledger line. It can only add a
  chance (RETRY, or an existing ROUTE). It can never change what a bail is.
- **The 2 stays a 2.** A bail after adjudication keeps its original cause and classification,
  so system and process failures stay apart (CLAUDE.md, "Exit codes are the API").
- **An eighth budget axis.** Folding adjudications into `VERI_STUCK_RETRIES` or `REVISE_BUDGET`
  would merge different failures into one decision (ADR-0020). `0` reproduces the behaviour from
  before this ADR.
- **Not every exit 2.** `killed-stuck` and `no-verdict` already have their own budgets.
  `killed-external` is a human's stop, and a preflight refusal is not a bail.
- **One rule, in one contingent unit.** `skills/tdd/ADJUDICATE.md` is read only on an eligible
  exit 2 (ADR-0019). Each site names it rather than restating it.
- **Fixed, small inputs.** The prompt carries the cause token, the command, the exit code, the
  last 50 lines of stderr, the allowed route tokens and the step's ledger line. It carries no
  leaf transcripts.

## Considered options

- **The conductor judges in its own context**: rejected. It leaves no record, it is not
  supervised, and it grows the conductor's context.
- **A repair outcome**: deferred. It needs writes and a guard of its own, and it should be
  decided once RETRY/ROUTE/BAIL hit rates are measured.
- **A per-step budget**: rejected. A step that keeps hitting exit 2 could loop.

## Consequences

- Sites gain adjudication one cause at a time (PRD 019.1–019.4, `ci-timeout` first).
- Every adjudication costs one opus leaf. `metrics.sh` reports that cost and the outcomes, so
  whether the judge pays for itself can be read off the report.
