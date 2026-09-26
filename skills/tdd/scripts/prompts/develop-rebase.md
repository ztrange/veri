{{SHARED}}

## Phase: develop-rebase

This run's branch is behind the default branch, and rebasing it onto `{{ONTO_SHA}}` stopped
on conflicts. That rebase was aborted, so the branch is back at `{{PRE_REBASE_SHA}}`, where it
stood before. Your job is to rebase it onto `{{ONTO_SHA}}` and resolve every conflict so that
both sides' intent survives.

### The files that conflicted

{{CONFLICTING_FILES}}

### The step this run was on

{{STEP}}

### The issue's behavior spec (context)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Rebase onto that exact commit, not onto a branch name that may have moved since:
   `git rebase {{ONTO_SHA}}`.
2. Resolve each conflict by reading both sides — `git log --oneline {{PRE_REBASE_SHA}}..{{ONTO_SHA}}`
   shows what the default branch added — then `git add` the file and `git rebase --continue`.
   If a conflict cannot be resolved without dropping one side's behaviour, run
   `git rebase --abort`, which returns the branch to `{{PRE_REBASE_SHA}}`, and report FAILED.
3. Confirm the test command is green on the rebased tip, through the wrapper
   `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to —
   `all`, since the whole test command is what runs:

       {{TIMED_TEST_RUN}} all '' {{TEST_CMD}}

   The wrapper hands the command's own exit status straight back, so a red run stays red.
4. Do not push. The conductor pushes and re-verifies the resolution.
5. Do not edit the ledger `.tdd/issue-<n>.md` beyond what the rebase itself carries: every
   `[x]` tick and every ` ⟂ refactor pending` mark must survive exactly as it is.

### Report (last lines of your output)

REBASE: RESOLVED | FAILED — <one line: which files conflicted and how you resolved them>
