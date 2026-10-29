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
   A conflict in a `*/GRADED` file is the exception: keep the replayed branch commit's side of
   every conflicted row by taking the file's `--theirs` side (mid-rebase `--ours` is the onto
   side, so it is the wrong one), edit no hash, and leave re-signing to the regrade block the
   conductor runs before `verify-rebase`. Resolved this way a `GRADED` conflict drops no
   behaviour, so it is no ground for FAILED. Never run `grade-prose.sh`, and never write or
   edit a `GRADED` hash by hand.
3. Confirm the test command is green on the rebased tip, through the wrapper
   {{INCLUDE:_timed-test-run-tier.md}} —
   `all`, since the whole test command is what runs:

       {{TIMED_TEST_RUN}} all '' {{TEST_CMD}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.
   One red is expected: a `prose-owed.sh` failure in that run, on a unit whose `GRADED` row the
   rebase touched, stays until the conductor regrades. It is not yours to fix and no ground to
   report `REBASE: FAILED`; any other red still is.
4. Do not push. The conductor pushes and re-verifies the resolution.
5. Do not edit the ledger `.tdd/issue-<n>.md` beyond what the rebase itself carries: every
   {{INCLUDE:_develop-ledger-tick.md}} {{INCLUDE:_develop-ledger-mark.md}}

REPORT-FORMAT rebase | keys REBASE: | suite exempt: the conductor re-verifies the resolution

### Report (last lines of your output)

REBASE: RESOLVED | FAILED — <one line: which files conflicted and how you resolved them>
