{{SHARED}}

## Phase: develop-revise (redoing diff)

{{INCLUDE:_develop-revise-opening.md}}

This step's criterion is a property of the branch's own diff, judged against the diff
alone, so no test is this step's deliverable.

### The step

{{STEP}}

### The verifier's rejection reason (address exactly this)

{{REJECTION_REASON}}

### The issue's behavior spec (context — the criterion above is what is in scope)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Read what this step left on disk and change it to answer that objection — and only
   that objection — then commit that change, its subject ending in `(#<issue>)`.
2. Add no test. A case that pins this criterion by reading another file's text or the git
   history is rejected.
3. Run the fast command, `{{FAST_CMD}}`, then the suites that `affected-suites.sh` prints
   for your change, each through the wrapper {{INCLUDE:_timed-test-run-tier.md}}:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   Finish only when both runs are green.
4. If the objection **cannot** be met — the criterion is already satisfied, or the reason
   asks for something the step cannot deliver — report `IMPOSSIBLE` and say why.

### Report (last lines of your output)

OUTCOME: REWRITTEN | IMPOSSIBLE — <what you changed, or why the step cannot be met as stated>
DIFF: <the change committed, in one line, or NONE>
SUITE: GREEN | RED — <the final summary line of that run>
