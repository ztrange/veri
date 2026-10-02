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
6. Two exceptions, for a step no test can observe — the only ones; each answers with a
   `PROOF:` line that stands in for the red test:
   - **`COVERED: unreachable`** — the step **only deletes code** (a prop, an effect, a
     function, a branch; it adds or moves nothing) and no mutation went red because **no
     caller reaches** that code. `PROOF:` names every caller and why none reaches the code or
     reads its value: no caller exists, every caller passes a no-op, the value is never read.
   - **`COVERED: type-only`** — the step changes **only types**: a type declaration, an
     annotation, a type export, all erased at compile, so the code that runs is byte-for-byte
     the same. Run the project's type checker (`npx tsc --noEmit`, `mypy`, …) and see it pass;
     `PROOF:` is exactly that command, one line, which the conductor reruns after the
     transform.

   A step that moves or reshapes runtime code is never `unreachable` or `type-only`, nor is
   code some caller still reaches and no test watches: that is `COVERED: no`.

### Report (last lines of your output)

COVERED: yes | no | unreachable | type-only
PROOF: <on unreachable, every caller and why none reaches the code; on type-only, the type-check command; NONE otherwise>
CAUGHT_BY: <the test that went red under the mutation, or NONE otherwise>
MUTATION: <the edit you made, in one line>
