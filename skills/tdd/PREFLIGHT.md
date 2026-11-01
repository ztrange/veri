## 0. Preflight — baseline checks (bail before any cycle)

These run **first**, before any cycle. If any fails, the baseline is poisoned —
**bail immediately**: report which check failed and stop (see `<base directory>/BAIL.md`). This is a degenerate bail (no
commits, nothing to revert or push) — just refuse to start. A red, dirty, or
unauthenticated baseline never gets a cycle.

**Every preflight refusal is recorded before the run stops.** Whichever check refused, on a first
launch or a resume, run `$S/preflight-refused.sh <n> <check>` once, naming the failing check (a
short name such as `dirty-tree`, `auth`, `leaf-launchable`, `baseline`, `tunables`, `leaf-models` or
`timeout`), and only then stop. It writes a `preflight-refused` event to the run's event log and posts
one issue comment naming the check, so a refused run is visible to `status.sh` and to a reader of the
issue, not only in the conductor's log.

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty. If dirty, **bail** with cause `needs-user`, asking the user in the bail comment to commit or stash (`Read` `<base directory>/BAIL.md`).
   The run no longer commits in this checkout — step 1.2 moves into a worktree that is clean
   by construction — but the check **stays**: the conductor still reads the issue and the
   default branch from here, and a dirty caller's checkout means something else is mid-work
   in it.
2. **`gh` and `claude` authenticated.** `gh api user` succeeds — the same REST route every
   other GitHub read here takes; a non-zero exit from it is a preflight failure, so report it
   and stop — and `claude auth status` reports `"loggedIn": true`. Every leaf is a `claude -p` subprocess: with an expired
   session each one fails at launch (`supervise.sh` exit 1 before any work), which is
   neither a verdict nor a hang and so has no bail classification — catch it here.
   Then run `$S/leaf-launchable.sh`, which asks the other half of the same question: not
   whether the binary would be *allowed* to work, but whether it starts at all. **Exit 2**
   means it does not — a guard refused the launch, the case `README.md`'s *Launching the
   conductor* describes (#187); veri never unsets `CLAUDECODE`, or any other such guard,
   itself — and is a preflight-class stop: report its stderr diagnostic
   verbatim and do not start. It runs **here**, before step 3, because the baseline is the
   expensive half of preflight and is wasted either way when no leaf can launch; a run that
   discovers this later has already paid for the suite, the worktree, the spec and a public
   `### ▶️ Resuming` comment on the issue thread.
3. **Suite is green at baseline — and time it — on the commit the cycles build on.** Enter
   the issue's worktree first, as step 1.2 describes — slug from the title, exit 2 a
   preflight-class stop — and clear any stale stop request there before anything else. The
   worktree's lock, `.tdd/conductor.pid`, is not yours to write: `run_conductor.py` writes the
   pid of the `claude -p` process it started into it before this preflight runs, and the
   conductor itself never writes it:
   ```
   wt="$($S/issue-worktree.sh <n> <slug>)" && cd "$wt"
   mkdir -p .tdd && $S/stop-requested.sh --clear
   rm -f .tdd/ci-conflict-rebased
   ```
   The `--clear` beside the lock drops a stale stop request a killed run never got to clear, so a
   `.tdd/stop` left behind cannot stop the run that resumes it at its first checkpoint. The `rm -f`
   drops a `.tdd/ci-conflict-rebased` an earlier run left, so the Draft PR step's one CI-conflict
   rebase is counted per run and a resume never inherits it.
   **Then, before the baseline, set the worktree up.** When the target repo's `CLAUDE.md`
   declares `veri: setup: <cmd>`, run `$S/worktree-setup.sh <n>` inside the run worktree on every
   start and every resume, with no condition on the ledger or on the last bail: a fresh worktree
   holds no installed dependencies of a nested package, so a suite can pass in it while the merge
   gate fails on a missing module, and the script itself runs `<cmd>` at most once per worktree.
   **Exit 3** means there is no such line, or setup is already done in this worktree: preflight is
   unchanged. **Exit 1** — the command exited non-zero — **bails** with cause `setup-failed`, a
   system failure, naming the command in the bail comment (see `<base directory>/BAIL.md`).
   **Exit 2** — no answer: bad arguments or an unreadable file — is a preflight-class stop:
   report its stderr diagnostic verbatim and do not start.
   A run that `issue-worktree.sh` handed back an existing worktree — which it marks by leaving
   the file `.tdd/handed-back` in that worktree; a freshly cut worktree has no such file, and
   whether the ledger `.tdd/issue-<n>.md` exists does not matter — first
   discards whatever a killed leaf left uncommitted, since a rebase refuses a dirty tree:
   ```
   stray="$($S/resume-clean.sh)"
   ```
   `resume-clean.sh` captures `git status --porcelain` and runs `git reset --hard HEAD`, so its
   stdout is the paths that reset discarded: keep it as `$stray` for sub-step 4 to
   name (`<base directory>/RESUME.md`). An exit 2 — an uncommitted `.tdd/` append it could not re-apply (kept
   in `kept-tdd-appends.diff`) or a failed git command — bails as a **system** failure
   (`no-verdict`, see `<base directory>/BAIL.md`).
   When a ledger exists, the script also reconciles it: a tick is committed with its step's green commit, so the committed ledger's ticks record which greens exist, and a working-copy `- [x]` line is kept ticked only when the committed
   ledger holds a tick of the same step text (the text without its trailing markers), so n committed ticks of a text keep at
   most n working ticks of it; every other `- [x]` line — its green commit is not on the branch — is unticked and loses its
   `⟂ refactor pending` mark, and every other working-copy line is kept as written.
   Then the handed-back run, its uncommitted `.tdd/` appends kept
   and its ledger ticks reconciled when a ledger exists, runs
   `$S/rebase-onto-default.sh` before its baseline, so the baseline runs on the rebased tip.
   On an exit 0 the first stdout line of `rebase-onto-default.sh` is `<pre-rebase-sha>`, the HEAD
   the branch held before the rebase. An exit 3 — the branch already contains `origin/<default>` — goes on unchanged. An exit 1 —
   the rebase conflicted and was aborted, HEAD untouched — goes on from the old base and
   leaves the conflict to the Draft PR step's `develop-rebase` path. An exit 2 bails as the
   Draft PR step's does, a **system** failure (`no-verdict`, see `<base directory>/BAIL.md`).
   An exit 0 moved the branch, and is marked in the run log as its own event,
   `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh resume-rebase from=<pre-rebase-sha> rebased="$(git rev-parse HEAD)"`,
   a name nothing the Draft PR step's rebase records shares.
   After that event, and before the baseline, run
   `$S/tests-frozen.sh rerecord-rebased .tdd/issue-<n>.md <pre-rebase-sha>`. Exit 0 or 3 goes on.
   **Exit 1** bails `needs-user`, a process failure: the bail comment quotes each
   `<case> (<owning step>)` line and says the branch changed a frozen earlier case for one of two
   reasons, naming both: the default branch also changed it, or the branch's own work (a refactor,
   say) changed it with the default branch untouched; the comment also tells the two apart. **Exit 2** bails `no-verdict`, a system failure
   (see `<base directory>/BAIL.md`).
   Only a run on a freshly cut worktree skips both the discard and the rebase here.
   Every run below happens in it, so the baseline proves the commit the branch is cut from —
   the freshly fetched `origin/<default>` for a new branch, the branch head on a resume — not
   whatever the caller's checkout has checked out.
   The issue may name its own test command,
   so read its body first — into a temp file, since the worktree must stay clean:
   ```
   body="$(mktemp)" && gh api repos/{owner}/{repo}/issues/<n> -q .body > "$body"
   ```
   Then, for `detach-command.sh`, get the fast tier's command from `$S/detect-test-command.sh --tier fast --issue "$body"` (see *Detecting the test command*),
   and run it through `$S/detach-command.sh start <name> <cmd>`, then `$S/detach-command.sh wait <name>` in the foreground with no max-seconds argument and the Bash tool's `timeout` of 600000 ms, calling `wait` again each time it returns 3 (never background it and end the turn).
   `detach-command.sh wait` answers 0 the command passed, 1 it finished red with its code on stdout (a red suite: stop and report), 2 it died recording nothing, 3 still running (call again). If already red, stop and report a preflight
   failure, whatever the caller's checkout holds — a cycle must not start on a red baseline. The one exception is a
   resume, whatever its last bail's cause: when its baseline is red only in suites that are red on the branch head but
   green on the default branch, preflight does not refuse. On the exit 0 of the check
   (`suite-red-resume.sh check`) the conductor inserts one `⟦suite-repair⟧` step naming those suites before
   the first unchecked step, commits the ledger and runs that step first; for the check, `Read` `<base directory>/RESUME.md`. A suite also red on the default branch still
   refuses as above. Reading the body **here**, before the baseline runs, is what
   keeps the baseline and every later leaf on one command: detected after the baseline, the
   issue's line would arrive too late to be the command the baseline proved green. Note how
   long the run took and keep it as `baseline`, the elapsed wall time in whole seconds
   (round up). This measurement is free — the run happens anyway — and it is taken once, so
   a suite that gets slower mid-run does not move the timeout under a leaf.
   Once that baseline is green, a resume rebase that moved the branch is published with
   `$S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, where `<pre-rebase-sha>`
   is the HEAD recorded before `rebase-onto-default.sh` ran. It is never a bare force: the
   pinned lease refuses the push when the remote branch is no longer the commit this run
   rebased from. A red baseline on the rebased tip resets the branch to `<pre-rebase-sha>`
   before the run bails, so a bailed resume leaves the branch on the commit it resumed from, not on a rebased tip no suite proved green (`Read` `<base directory>/BAIL.md`).

   **Then time the full tier too.** Get its command from
   `$S/detect-test-command.sh --tier all --issue "$body"`, run it once through `detach-command.sh` in the same start-then-wait shape as the preflight baseline,
   and keep its elapsed
   wall time in whole seconds (round up) as `full`; step 7 sizes the run's hard timeout from
   that number, not from `baseline`. The full-tier run is the work a leaf actually does — a
   verifier runs this very command and a developer leaf runs the suites covering the files it
   touched — while no leaf runs the fast tier at all, so a timeout timed off the fast one
   bounds work nobody does: that is how #300's green leaf was killed at the 900 s floor
   twice over while it was working. It is timed here, with the same single-measurement rule,
   and costs one full-tier run the Draft PR gate pays for anyway. If it is red, stop and
   report, for the same reason a red fast tier stops the run.
4. **Default branch.** Capture it for the PR base:
   `gh api repos/{owner}/{repo} -q .default_branch`.
5. **Tunables parse.** Run `$S/refactor-budget.sh 0` once. **Exit 2** means
   `VERI_REFACTOR_BUDGET` is not a whole number ≥ 0 — stop and report its stderr diagnostic
   verbatim. A budget that cannot be read is a poisoned baseline like a red suite, not a
   decision, and catching it here is what lets the refactor loop treat exit 2 as impossible.
   Exit 0 and exit 3 both mean it parses (3 only says the budget is 0 — a run with the
   refactor loop switched off), so continue.

   Then run `$S/refactor-budget.sh --issue 0` once, which reads `VERI_ISSUE_REFACTOR_BUDGET`,
   the structural pass's budget, the same way: **exit 2** is the same stop, its stderr
   reported verbatim; exit 0 and exit 3 both mean it parses.

   Then the plan-growth budget, which `add-ledger-step.sh` reads the same way: it must be
   unset, or a whole number ≥ 0. There is nothing to run, since that script refuses an
   anchor it cannot find before it ever looks at the budget, so read the value here:
   ```
   [[ -z "${VERI_STEP_GROWTH+x}" || "$VERI_STEP_GROWTH" =~ ^[0-9]+$ ]]
   ```
   False — anything else, **including set-but-empty** — is the same **exit 2** as a bad
   `VERI_REFACTOR_BUDGET`: stop and do not start, reporting the value verbatim. Caught here
   it costs nothing; left to the first leaf that tries to grow the plan, it surfaces as a
   refused insertion mid-cycle, with the branch, the worktree and the plan already built.

   Then the missing-reroute budget, which `wrong-test-route.sh` reads: it must be unset, or a
   whole number ≥ 0 (unset means 3):
   ```
   [[ "${VERI_MISSING_REROUTE_BUDGET:-3}" =~ ^[0-9]+$ ]]
   ```
   False is the same **exit 2** as a bad `VERI_STEP_GROWTH`: stop and do not start, reporting the
   value verbatim. It is a seventh budget axis, never folded into `REVISE_BUDGET`,
   `VERI_STUCK_RETRIES`, `VERI_NO_VERDICT_RETRIES`, `VERI_REFACTOR_BUDGET`, `VERI_STEP_GROWTH` or
   `VERI_SKILL_EDIT_BUDGET`.

   Then the two money budgets: run `$S/step-budget.sh` once, with no arguments. **Exit 2**
   means `VERI_STEP_BUDGET` or `VERI_RUN_BUDGET` is not a non-negative decimal number — the
   same preflight-class stop as a bad `VERI_REFACTOR_BUDGET`: report its stderr diagnostic
   verbatim and do not start, before any leaf is launched. Exit 0 prints the step budget,
   then the run budget, one per line.
6. **Leaf models parse.** Run `$S/leaf-model.sh develop-red`,
   `$S/leaf-model.sh revise-green` and `$S/leaf-model.sh verify-green` once each. All three,
   because the four variables do not all reach every name: `VERI_MODEL_DEVELOPER` is only
   ever read for a developer name, `VERI_MODEL_REVISE` only for a revise one and
   `VERI_MODEL_VERIFIER` only for a verifier one, so a preflight that skipped a name would
   let that name's bad value through and kill every leaf it governs at launch.
   A variable that is empty or whitespace-only is treated as unset, so it never stops the run.
   Only a value with internal whitespace stops it — and a word with a leading or trailing space counts (`sonnet 5`, `" sonnet"`, `"sonnet "`): **exit 2** means the value cannot be a
   model name — `sonnet 5` is two words where the CLI takes one — and is a preflight-class
   stop like step 5: report its stderr diagnostic verbatim and do not start. The resolver is
   otherwise first called at launch, by which time the branch, the worktree and the plan
   already exist and a typo costs a bail to undo. Exit 0 means continue.
7. **Size the run's hard timeout from the full-tier measurement.** Hand step 3's `baseline`
   and its `full` measurement to `$S/leaf-timeout.sh`, so every leaf of the run is launched
   under the result rather than under the supervisor's fixed 900 s default:
   ```
   timeout="$($S/leaf-timeout.sh "$baseline" --full "$full")"
   ```
   `--full` says which of the two measurements the timeout is sized from: the full-tier one
   displaces the fast one rather than mixing with it, because a leaf runs the full tier and
   never the fast one.
   The script keeps a quick suite on today's 900 s and gives a slow one 6 × its baseline —
   which is what stops a leaf whose own test command takes minutes being killed as stuck
   while it is working (#71: a 900 s cap against a 140-250 s suite, two bails, both steps
   reverted). An export would not survive: every Bash call is a fresh shell. So step 1.2,
   once it has entered the issue's worktree, calls the script again with the issue number,
   which records the settled number once per issue in `.tdd/issue-<n>-timeout` at the run
   worktree's root, and `supervise.sh` reads that file whenever `VERI_TIMEOUT` is unset —
   in every phase of every cycle below, and after a resume, without re-measuring; no launch
   line has to pass it. An explicit `VERI_TIMEOUT` is printed back as given, so setting one by hand still
   wins and the liveness axis stays yours. **Exit 2** means the number could not be read —
   a malformed measurement, or an explicit `VERI_TIMEOUT` that is not a whole number ≥ 1 —
   and is a preflight-class stop like step 5: report its stderr diagnostic verbatim and do
   not start, because a run whose timeout is garbage kills every leaf it launches.

