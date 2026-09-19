# Generality comes from triangulation; refactor is behavior-preserving

**Superseded in part by [ADR-0021](0021-green-is-obvious-implementation.md)**: green does
not fake. The "fake-green" half of the Context below no longer holds; triangulation as the
only route to generality does. The triangulating step the refactor leaf "confirms" is now
added to the ledger by [ADR-0022](0022-the-ledger-grows-mid-run.md).

Production code is only ever added to satisfy a failing test. Generality is achieved by
**triangulation** — each acceptance criterion becomes a failing test (a plan step), and
the implementation is forced to generalize to keep all of them green. The refactor step
is strictly **behavior-preserving** (structure, conventions, typing, robustness of code
already covered by tests); it never adds untested branches. When the refactor leaf spots
overfit/hardcoded code, it does not "fix" it — it flags that another triangulating step
is needed, and confirms the plan contains one.

## Context

The user asked that code "work for general cases, not just the single test," which pulls
against "no code without a failing test." Resolved in favor of strict TDD (matches the
reference suite's fake-green + triangulate discipline): hand-added generality is untested
code the blind verifier has nothing to pin down. Rejected: letting refactor generalize
while the suite stays green (introduces untested paths), and a self-triangulating
generality leaf (extra machinery, plan scope-creep) — the latter remains a possible later
addition.

## Consequences

The plan/scope leaf owns generality: it must enumerate enough acceptance criteria that
triangulation forces the general implementation. Under-triangulation leaves code overfit;
the refactor leaf surfaces that as a missing-step signal rather than silently widening the
code. This keeps every line traceable to a test and keeps the blind verifier meaningful.
