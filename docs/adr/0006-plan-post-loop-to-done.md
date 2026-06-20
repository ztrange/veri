# Plan, post the plan to the issue, then loop to done

The conductor handles an issue by decomposing it into a **plan** — a checklist of small
steps, each a single TDD cycle's worth and aligned to the issue's acceptance criteria —
posting that checklist as a comment on the issue, then looping over it (one Red→Green→
Refactor cycle per step) until every acceptance criterion is covered and the issue is
done. There is no hard "too big" bail: bigness is handled by splitting into more steps,
all worked within the one run.

## Context

The user's flow is "create a comment with the plan to split the work and loop over that
plan until the issue is done." Size is treated as informational — surfaced in the plan
comment — rather than a gate. This mirrors the reference suite's `tdd-deliver` (decompose
a PLAN item into TODO items, loop), but the worklist lives in the issue thread (ADR-0005)
instead of a local `TODO.md`.

## Consequences

The done-condition is "all plan steps complete / all acceptance criteria covered" — this
is the same loop that later answers "when is the issue finished." A pathologically huge
issue will simply run long; a future safety valve (escalate or suggest splitting into
separate dependency-marked issues) can be added without changing this shape. Whether the
loop's state of record is the issue comment, a local file, or both is resolved separately
(it bears on crash-resumability).
