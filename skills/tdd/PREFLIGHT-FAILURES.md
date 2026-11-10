## 0. Preflight — failure branches

What each preflight check does when it fails. The checks and their order are in
`<base directory>/PREFLIGHT.md`; bails are classified in `<base directory>/BAIL.md`.

**Any failure poisons the baseline.** If any preflight check fails, the baseline is poisoned: report
which check failed and stop. This is a degenerate bail — no commits, nothing to revert or push — and a
red, dirty or unauthenticated baseline never gets a cycle.

**Every refusal is recorded.** A preflight refusal writes a `preflight-refused` event naming the failing
check and posts one issue comment naming it (`$S/preflight-refused.sh <n> <check>`), so a refused run is
visible to `status.sh` and to a reader of the issue, not only in the conductor's log.

### Check 1 — repo and clean tree

If the caller's checkout is dirty, stop and ask the user to commit or stash.

### Step 2 — authentication and launch

- A failing `gh api user` (the REST route), or a `claude auth status` that is not `"loggedIn": true`, is
  a preflight failure: report it and stop.
- An exit 2 from `leaf-launchable.sh` stops the run, and its stderr diagnostic is reported verbatim. It
  is the case the README's *Launching the conductor* section describes (#187). veri never unsets
  `CLAUDECODE` or any other launch guard itself.

### Step 3 — worktree, resume and baseline

- `worktree-setup.sh`: exit 1 (`<cmd>` exited non-zero) **bails** with cause `setup-failed`, a system
  failure, naming the command. Exit 2 (no answer: bad arguments or an unreadable file) is a
  preflight-class stop.
- `resume-clean.sh` exit 2 (an uncommitted `.tdd/` append it could not re-apply, kept in
  `kept-tdd-appends.diff`, or a failed git command) bails as a system failure with cause `no-verdict`.
- The resume rebase: exit 2 bails as a system failure (`no-verdict`).
- `tests-frozen.sh rerecord-rebased`: exit 1 bails `needs-user`, a process failure. The bail comment
  quotes each `<case> (<owning step>)` line and says the branch changed a frozen earlier case for one of
  two reasons, naming both: the default branch also changed it, or the branch's own work (a refactor,
  say) changed it with the default branch untouched; it also tells the two apart. Exit 2 bails
  `no-verdict`, a system failure (see `<base directory>/BAIL.md`).
- `detach-command.sh wait` answers 1 when it finished red with its code on stdout (a red suite: stop
  and report) and 2 when it died recording nothing. A 2 while `$S/stop-requested.sh` exits 0 and prints
  `now` is the stop being carried out: not a preflight failure and not a poisoned baseline. The
  conductor goes to *Stopping* (`Read` and run `<base directory>/STOPPING.md`), records a `stop` event
  and no `bail`, and posts no preflight refusal. A wait that exits 2 while no `now` stop is pending is
  still read as the failure it reports.
- A red baseline stops the run as a preflight failure, whatever state the caller's checkout is in. A red
  output naming no test target, or any target still red alone, stops the run.
- A red full tier stops the run. A red output naming no test target, or any target still red alone, stops the run.
- A red baseline on the rebased tip resets the branch to `<pre-rebase-sha>` before the run bails.
- **The one exception: a resume with a suite-only red baseline.** When the resume's baseline is red only
  in suites that are red on the branch head but green on the default branch, preflight does not refuse,
  whatever the previous bail's cause (`revise-exhausted` included). The conductor inserts one
  `⟦suite-repair⟧` step naming those suites before the first unchecked step, commits the ledger and runs
  that step first — except that when those suites are red only because a unit's `GRADED` signature is
  stale and that unit has a pending `⟦skill-edit⟧` step, it inserts no repair step and that step runs
  first. A suite also red on the default branch still refuses as above.

### Step 5 — tunables

Each of these is a preflight stop before any leaf is launched:

- `refactor-budget.sh 0`: exit 2 (`VERI_REFACTOR_BUDGET` not a whole number ≥ 0) stops the run,
  reporting its stderr verbatim.
- `refactor-budget.sh --issue 0`: exit 2 is the same stop.
- `VERI_STEP_GROWTH` set-but-empty, or any other value that is not a whole number ≥ 0, is an exit-2
  stop, reporting the value verbatim.
- `VERI_MISSING_REROUTE_BUDGET` failing its check (false) is an exit-2 stop that reports the value
  verbatim.
- `VERI_SKIP_VERIFY`: any word that is not a phase this release can skip, or is `plan`, exits 2 before
  the baseline, naming it.
- `step-budget.sh` exit 2 means `VERI_STEP_BUDGET` or `VERI_RUN_BUDGET` is not a non-negative decimal
  number: a stop reporting its stderr diagnostic verbatim.

### Step 6 — leaf models

- An exit 2 from `leaf-model.sh` stops the run with the diagnostic reported.
- Any model variable value containing whitespace other than an empty or whitespace-only one — internal,
  or a leading or trailing space (`sonnet 5`, `" sonnet"`, `"sonnet "`) — is exit 2: a preflight stop
  reporting the diagnostic verbatim. An empty or whitespace-only value counts as unset.

### Step 7 — timeout

A leaf-timeout exit 2 stops the run with its diagnostic reported verbatim.
