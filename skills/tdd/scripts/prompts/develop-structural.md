{{SHARED}}

## Phase: develop-structural

This is the issue's **structural pass**: every step is green, and the structural candidates
the steps recorded instead of applying are now due. Apply the **one candidate** below and
commit it. Behaviour does not change: every test that was green stays green, and **no test
file is touched**.

### The candidate to apply

{{STEP}}

### Bounds

Change only the files this issue touched:

{{TOUCHED_FILES}}

A transform that needs a file outside that list is not this pass's to apply: leave the tree
as you found it and say so in your report.

### The issue's behavior spec (context only)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Apply exactly the candidate above — no other transform, no behaviour change.
2. Run the suites covering the files you touched, through the wrapper `{{TIMED_TEST_RUN}}`:

       {{TIMED_TEST_RUN}} affected '<the suites you ran>' <the command that runs them>

   They must stay green.
3. Commit this one transform as its own `refactor:` commit. Never modify a test file: a
   transform commit that touches one is rejected.

### Report (last lines of your output)

TRANSFORM: <the refactoring applied, in one line>
SUITE: GREEN | RED — <the final summary line of that run>
