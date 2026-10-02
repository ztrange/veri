{{SHARED}}

## Phase: develop-cover

This is a **refactor** run: the issue's subject is structure, not behaviour, so the step
below names one refactoring to apply later, in the transform phase. Before anything moves,
establish whether the behaviour of the code that step will move is **covered** — whether
some existing test goes red when that behaviour breaks. Write **NO** production code and
**NO** test.

### The step to cover

{{STEP}}

### The issue's behavior spec (context only)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Read the step and find the code it will move or reshape.
2. Copy the file first — `cp <file> <file>.orig` — then **break its behaviour by hand**
   with a minimal edit to that production code — remove a
   guard, invert a condition, drop a branch.
3. Run the suites that cover that code, through the wrapper `{{TIMED_TEST_RUN}}`:

       {{TIMED_TEST_RUN}} affected '<the suites you ran>' <the command that runs them>

   Expect red. Note the test that caught the mutation.
4. **Restore** the file exactly — `mv <file>.orig <file>` — and prove the edit is gone: `git diff`
   must print what it printed before the mutation. The working tree must be exactly as you found it.
5. If no mutation you can make turns any test red, the code is not covered: report
   `COVERED: no`. Do not write a test to cover it — that is not this phase's work.

### Report (last lines of your output)

COVERED: yes | no
CAUGHT_BY: <the test that went red under the mutation, or NONE on no>
MUTATION: <the edit you made, in one line>
