{{SHARED}}

## Phase: develop-cover

This is a **refactor** run: the issue's subject is structure, not behaviour, so the step
below names one refactoring to apply later, in the transform phase. Before anything moves,
establish whether the behaviour of the code that step will move is **covered** — whether
some existing test goes red when that behaviour breaks. Write **NO** production code and
**NO** test.

### The step to cover

{{STEP}}

{{INCLUDE:_develop-spec-context-only.md}}

1. Read the step and find the code it will move or reshape.
2. Copy the file first — `cp <file> <file>.orig` — then **break its behaviour by hand**
   with a minimal edit to that production code — remove a
   guard, invert a condition, drop a branch.
3. Run the suites that cover that code, through the wrapper `{{TIMED_TEST_RUN}}`:

       {{INCLUDE:_timed-test-run-affected.md}}

   Expect red. Note the test that caught the mutation.
4. **Restore** the file exactly — `mv <file>.orig <file>` — and prove the edit is gone: `git diff`
   must print what it printed before the mutation. The working tree must be exactly as you found it.
5. If no mutation you can make turns any test red, the code is not covered: report
   `COVERED: no`. Do not write a test to cover it — that is not this phase's work.
6. Answer `COVERED: unreachable` only for a step that only deletes code no caller reaches,
   with a `PROOF:` naming every caller and why none reaches the code: none exists,
   every caller passes a no-op, or the value is never read.
7. Answer `COVERED: type-only` only for a step that changes only types, with a `PROOF:`
   that is the type-check command you ran green: `npx tsc --noEmit`, `mypy`, or the
   repository's own.
8. A step that moves or reshapes runtime code is never `unreachable` or `type-only`;
   reachable code no test watches is `COVERED: no`.

REPORT-FORMAT cover | keys MUTATION: COVERED: CAUGHT_BY: PROOF: | suite exempt: the leaf mutates and reverts, it runs no suite to report

### Report (last lines of your output)

MUTATION: <the edit you made, in one line>
COVERED: yes | no | unreachable | type-only
CAUGHT_BY: <the test that went red under the mutation, or NONE on no>
PROOF: <the callers and why none reaches the code, or the type-check command you ran green; NONE otherwise>
