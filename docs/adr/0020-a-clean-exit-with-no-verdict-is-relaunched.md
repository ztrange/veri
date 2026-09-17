# A verifier that exits cleanly with no verdict is relaunched, not bailed

ADR-0011 and `SKILL.md`'s exit-2 branch ("Malformed / killed-stuck (exit 2)") say that
`verify.sh` exit 2 is a **bail**, classified as a `no-verdict` system failure. This record
**narrows** that: when the verifier leaf was **not killed** — `supervise.sh` reported success —
and `parse-verdict.sh` finds no `VERDICT:` line at all, `verify.sh` **relaunches** the verifier
on a fresh attempt, up to `VERI_NO_VERDICT_RETRIES` times (default 1). Only when that budget is
spent does it exit 2, and only then does the conductor bail as before. A verifier killed by
`supervise.sh` (stuck, hard timeout) is still exit 2 at once: its relaunches are
`VERI_STUCK_RETRIES`, spent inside the supervisor, and `verify.sh` adds no layer on top.

## Context

On #212's step 1 the verifier leaf launched `make test` as a background call and ended its
turn to wait for a notification that a `claude -p` leaf never receives. It exited cleanly,
never rendered a verdict, and the run bailed with a green implementation already on disk. The
foreground rule was already in the prompt (#162) and the leaf broke it anyway: a prompt rule
lowers the rate, and something downstream has to absorb the case where the model ignores it.

A relaunch is safe because the verifier is blind: it takes only the phase, the spec, the test
path and the test id, re-runs the suite itself, and its prompt is byte-identical on every
attempt. It judges the same tree from scratch and cannot inherit the failed attempt's reasoning.

## Decision

- A clean exit with no verdict is relaunched; the event log records it under a cause distinct
  from a leaf killed before it could render one, on each relaunch and on the final exit 2.
- `VERI_NO_VERDICT_RETRIES` is a **fourth budget axis**, never merged with
  `VERI_STUCK_RETRIES`. Stuck retries answer *liveness* — the process never finished; this
  answers *protocol compliance* — the process finished and ignored the output contract. They
  fail for different reasons, are fixed in different places and are tuned on different evidence.
- `metrics.sh` counts these relaunches as their own column, neither a retry nor a revise.

## Consequences

A single contract breach no longer costs a whole run. A verifier that breaches it on every
attempt still bails, as a system failure, exactly as ADR-0011 describes.
