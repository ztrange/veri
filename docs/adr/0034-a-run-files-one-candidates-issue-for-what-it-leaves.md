# A run files one candidates issue for what it leaves

Partly reverses **ADR-0031** ("a run does a refactor now, or drops it; it never files one").
A run still applies what it can in the issue that found it, but what it leaves, every
`out-of-bounds` row and every `not-done` row of `.tdd/issue-<n>-refactor-owed.md`, is filed
as one issue, `Refactor candidates left by #<n>`, at the Draft PR step.

## Context

ADR-0031 made every candidate a run did not apply visible only in its PR body, where the
coordinator cannot groom or decide on it without reading each PR. Before ADR-0031, runs
filed 118 per-candidate issues. Of the 51 runs after ADR-0031, 2 had a leftover (#1980 and
#2206).

## Decision

- One issue per run, at most, titled `Refactor candidates left by #<n>`, labelled `refactor`
  and `refactor-owed`. A resume finds it by its exact title and replaces its body.
- Outside the queue: it is never opted in (never `VERI_LABEL`, never `ready-for-agent`), so
  it never enters the solvable set.
- Groomed by `/vgroom --refactor-owed`, which the coordinator runs to decide on each row.
- `applied` and `test-only` rows are not filed: nothing is owed.

## Rejected alternative

One issue per candidate, the 118 before ADR-0031: each closed its feedback loop days later,
in another run, against code that had moved on, and flooded the tracker. The 51-run
measurement shows the leftover is rare (2 of 51 runs), so one issue per run costs the
coordinator almost nothing.

## Consequences

The tracker gains at most one groomable issue per run that left something, and none for a
run that left nothing.
