{{SHARED}}

## Phase: develop-reconcile

`push-branch.sh` could not push this run's branch: git rejected it as a non-fast-forward.
The remote branch `origin/{{BRANCH}}` is at `{{REMOTE_SHA}}`, which the local branch does
not contain. Your job is to make the push land without losing anyone's commits.

### The step this run was on

{{STEP}}

### The issue's behavior spec (context)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Review the divergence in both directions:
   - `git log --oneline {{REMOTE_SHA}}..HEAD` — what the run has that the remote does not
   - `git log --oneline HEAD..{{REMOTE_SHA}}` — what the remote has that the run does not
2. Decide whose commits the remote holds:
   - **Commits the run does not have** (someone else's work, or anything that is not this
     run's own earlier history): rebase onto the remote with
     `git rebase {{REMOTE_SHA}}`, confirm the test command is still green, then
     `git push origin HEAD:{{BRANCH}}`.
     Make that green check through the wrapper `{{TIMED_TEST_RUN}}`, which records what the
     run cost and names the tier it belongs to — `all`, since the whole test command is what
     runs:

         {{TIMED_TEST_RUN}} all '' {{TEST_CMD}}

     The wrapper hands the command's own exit status straight back, so a red run stays red.
   - **Only the run's own pre-rebase history** (the same commits, rewritten locally): push
     with the lease pinned to the sha above, and nothing looser:
     `git push --force-with-lease={{BRANCH}}:{{REMOTE_SHA}} origin HEAD:{{BRANCH}}`.
3. Never force-push any other way: no unpinned lease, and no plain force flag. If the
   pinned push is itself rejected, the remote moved again — stop and report it.
4. Do not edit the ledger `.tdd/issue-<n>.md`: every `[x]` tick and every
   ` ⟂ refactor pending` mark must survive exactly as it is.

### Report (last lines of your output)

RECONCILE: REBASED | FORCED | FAILED — <one line: what the remote held and what you did>
