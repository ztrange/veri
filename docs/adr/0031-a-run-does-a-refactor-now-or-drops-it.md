# A run does a refactor now, or drops it; it never files one

Extends **ADR-0017** (one refactor leaf per step, bounded by `VERI_REFACTOR_BUDGET`) to the
structural pass before the PR is readied. A refactor candidate the pass finds is either
applied in the issue that found it or listed in the PR body under `### Not done` with its
reason: `budget spent`, `no predicate`, `transform rejected` or `uncovered`. No
`Refactor owed by #<n>` issue is filed and no existing one is commented on;
`refactor-overflow.sh`, its module and its suites are removed.

## Context

101 `Refactor owed by` issues were filed by runs that found a refactor and left it. Each closed
its feedback loop days later, in another run, against code that had moved on. A refactor
belongs in the original issue, where the feedback loop stays as close and quick as XP wants.

## Decision

- An out-of-scope candidate is listed for the pass like any other. Its transform leaf is
  bounded to the issue's touched files plus the files the candidate names, enforced
  mechanically before its verifier runs.
- Widening the pass to files the run's tests never exercised would hide a behaviour change in
  them, so a cover leaf mutates the code the candidate will move first; `COVERED: no` launches
  no transform and the candidate is reported `uncovered`.
- `VERI_ISSUE_REFACTOR_BUDGET` defaults to **10**, up from 3. It stays its own axis, never
  merged with `VERI_REFACTOR_BUDGET` (the per-step cost budget of ADR-0017), for the reason
  **ADR-0020** gives for keeping budgets apart: one knob over two would make different
  failures one decision. A bad value still exits 2 in preflight.

## Consequences

A candidate the run cannot do is visible in the PR it belongs to and then gone; nothing
accumulates in the tracker. A larger default budget lets the pass finish more of what it
finds, at the cost of a longer pass on a refactor-heavy issue.
