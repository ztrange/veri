# Rung 3 is N supervised print-mode conductors over one object store

Rung 3 of the scope ladder — several issue-conductors at once over the solvable set — is
`parallel-conductors.sh`: rung 2's loop with one more word, **in flight**. It launches up to
`VERI_PARALLEL` conductors, each `run-conductor.sh <n>` detached under its own `supervise.sh`
as `conductor-<n>`, every one in its own worktree `.tdd/wt/<n>` (ADR-0013) over the one
object store of the caller's clone. The in-flight set lives in the launcher. A run's outcome
is read from its PR and its event log, never from its exit code.

## Context

Until #102 several threads ran only because an operator started one `run-conductor.sh` per
shell and remembered which issues were already taken. Everything a parallel launcher needs
below selection already existed: worktree isolation (ADR-0013) and its pid guard (#170), a
selection that leaves claimed and blocked issues out (`solvable-issues.sh`), a claim every
machine can see (the draft PR, ADR-0024), and detach-then-wait (`supervise.sh`,
`wait-leaf.sh`). What the hand-run recipe got right by remembering it — the caller's leaf
tunables reaching each conductor unchanged, the launcher's files never dirtying the caller's
checkout — the script has to get right by construction.

## Decision

- **N supervised print-mode conductors.** Each conductor is a leaf-shaped process under
  `supervise.sh`, whose heartbeat and timeout are both `VERI_RUN_TIMEOUT` with no stuck
  retries: a conductor's stdout is silent for the length of a leaf, so a shorter outer
  heartbeat kills a healthy run. A killed conductor is not retried; its ledger is committed
  and `/tdd <n>` resumes it. `VERI_PARALLEL` defaults to 1 because N conductors are N
  concurrent `claude -p` sessions, billed as such.
- **The in-flight set lives in the launcher**, local to one invocation: the numbers it
  launched and has not seen finish, subtracted from each fresh `solvable-issues.sh` print.
  It is re-selected after every completion, in printed order, and never launches one number
  twice in an invocation.
- **Outcomes come from the PR and the event log.** `claude -p` exits 0 on a finished run, a
  bail and a SIGTERM alike, and after ADR-0024 both a finished and a bailed run leave an open
  PR. So a **ready** PR is *done*, a **draft** PR whose run's `.tdd/events.jsonl` ends in a
  bail is *bailed*, and a supervisor exit 2 is *killed after `VERI_RUN_TIMEOUT` s*.

### Rejected

- **A remote claim written at launch** — a label, a comment or a pushed ref marking the issue
  taken the moment a conductor starts. The draft PR the conductor opens after its plan commit
  (ADR-0024) already is one, visible to every machine; a second claim would outlive a crashed
  launcher with nothing to clear it, and would have to be kept in step with the first.
- **Reading the outcome from the exit code.** It cannot carry one: see above.

## Consequences

- Two launchers on one label still collide inside ADR-0024's accepted window, since each sees
  only its own in-flight set. The answer stays one label per launcher.
- N conductors run N `make test` baselines in the same checkout at once. veri's suites work in
  `mktemp` dirs; a target whose suite writes fixed paths inside the repo will race with itself,
  and that is the target's test command to fix, not the launcher's to guess.
