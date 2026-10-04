{{SHARED}}

## Phase: develop-revise (redoing diff)

A previous attempt at this step was **rejected** by the blind verifier. You are a fresh
leaf: you never saw that attempt or its reasoning, so the rejection reason below is the
whole of what you have to work from. The work it left is on disk — read it, then fix
exactly what the reason objects to.

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
   that objection — then commit that change.
2. Add no test. A case that pins this criterion by reading another file's text or the git
   history is rejected.
3. Run the suites covering the files you touched, through the wrapper `{{TIMED_TEST_RUN}}`:

       {{TIMED_TEST_RUN}} affected '<the suites you ran>' <the command that runs them>

   They must stay green.
4. If the objection **cannot** be met — the criterion is already satisfied, or the reason
   asks for something the step cannot deliver — report `IMPOSSIBLE` and say why.

### Report (last lines of your output)

OUTCOME: REWRITTEN | IMPOSSIBLE — <what you changed, or why the step cannot be met as stated>
DIFF: <the change committed, in one line, or NONE>
SUITE: GREEN | RED — <the final summary line of that run>
