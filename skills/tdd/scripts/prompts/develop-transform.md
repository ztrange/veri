{{SHARED}}

## Phase: develop-transform

This is a **refactor** run, and the cover phase has shown the code this step moves is
covered. Apply the **one named refactoring** below and commit it. Behaviour does not
change: every test that was green stays green, and **no test file is touched**.

### The refactoring to apply

{{STEP}}

The step's criterion is a shell predicate stating the smell: false before this step, true
after. It is the step's red; your transform is what makes it true.

### The issue's behavior spec (context only)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Apply exactly the refactoring the step names — no other transform, no behaviour change.
2. Run the step's predicate and confirm it now holds.
3. Run the suites covering the files you touched, through the wrapper `{{TIMED_TEST_RUN}}`:

       {{TIMED_TEST_RUN}} affected '<the suites you ran>' <the command that runs them>

   They must stay green.
4. Commit the transform. Never modify a test file: a transform commit that touches one is
   rejected.

### Report (last lines of your output)

TRANSFORM: <the refactoring applied, in one line>
PREDICATE: HOLDS | FAILS
SUITE: GREEN | RED — <the final summary line of that run>
