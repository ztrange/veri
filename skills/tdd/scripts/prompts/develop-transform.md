{{SHARED}}

## Phase: develop-transform

This is a **refactor** run, and the cover phase has shown the code this step moves is
covered. Apply the **one named refactoring** below and commit it. Behaviour does not
change: every test that was green stays green, and **no test file is touched**.

### The refactoring to apply

{{STEP}}

The step's criterion is a shell predicate stating the smell: false before this step, true
after. It is the step's red; your transform is what makes it true.

{{INCLUDE:_develop-spec-context-only.md}}

1. Apply exactly the refactoring the step names — no other transform, no behaviour change.
2. Run the step's predicate and confirm it now holds.
3. {{INCLUDE:_develop-run-affected.md}}
4. Commit the transform. Never modify a test file: a transform commit that touches one is
   rejected.

{{INCLUDE:_develop-transform-report.md}}
PREDICATE: HOLDS | FAILS
SUITE: GREEN | RED — <the final summary line of that run>
