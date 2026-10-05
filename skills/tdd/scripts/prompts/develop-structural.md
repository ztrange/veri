{{SHARED}}

## Phase: develop-structural

{{INCLUDE:_develop-structural-pass.md}} Apply the **one candidate** below and
commit it. Behaviour does not change: every test that was green stays green, and **no test
file is touched**.

### The candidate to apply

{{STEP}}

### Bounds

Change only the files this issue touched:

{{TOUCHED_FILES}}

A transform that needs a file outside that list is not this pass's to apply: leave the tree
as you found it and say so in your report.

{{INCLUDE:_develop-spec-context-only.md}}

1. Apply exactly the candidate above — no other transform, no behaviour change.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit this one transform as its own commit, as `refactor: <what changed> (#<issue>)`.
   Never modify a test file: a transform commit that touches one is rejected.

{{INCLUDE:_develop-transform-report.md}}
SUITE: GREEN | RED — <the final summary line of that run>
