## 0. Preflight — baseline checks (bail before any cycle)

These run **first**, before any cycle: a red, dirty, or unauthenticated baseline never gets a cycle.

When a preflight check refuses (a failing check, a red baseline or full tier, or any exit the check
names as a stop or a bail), `Read` `<base directory>/PREFLIGHT-FAILURES.md` then and not before, and
run it. A preflight that passes never reads it.

**The script ran before this file was read.** `SKILL.md` step 0 runs `$S/preflight.sh <n> <slug>`
first, and this file is read only when it exits neither 0 nor 3. The script runs a fresh run and a
resume alike, so a fresh run and a resume both continue from the step the script's last line names,
by the steps below. Steps 1 to 7 stay stated here.

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty.
   The run no longer commits in this checkout — step 1.2 moves into a worktree that is clean
   by construction — but the check **stays**: the conductor still reads the issue and the
   default branch from here, and a dirty caller's checkout means something else is mid-work
   in it.
2. **`gh` and `claude` authenticated.** `gh api user` succeeds — the same REST route every
   other GitHub read here takes — and `claude auth status` reports `"loggedIn": true`. Every leaf is a `claude -p` subprocess: with an expired
   session each one fails at launch (`supervise.sh` exit 1 before any work), which is
   neither a verdict nor a hang and so has no bail classification — catch it here.
   Then run `$S/leaf-launchable.sh`, which asks the other half of the same question: not
   whether the binary would be *allowed* to work, but whether it starts at all. It runs **here**, before step 3, because the baseline is the
   expensive half of preflight and is wasted either way when no leaf can launch; a run that
   discovers this later has already paid for the suite, the worktree, the spec and a public
   `### ▶️ Resuming` comment on the issue thread.
   Last, once the authentication and launch checks pass and before step 3 creates the issue's
   worktree, run `$S/ready-check.sh --no-suites` on the target repo: the readiness table
   `/vready` prints, without the test-tier runs step 3 makes anyway. A failing `fast tier`,
   `all tier`, `pull_request`, `gh auth`, `push access` or `label <VERI_LABEL's value>` row
   stops the run with exit 1, and a `ready-check.sh` that gives no answer (its exit 2) stops it
   with exit 2; any other failing row is printed and the run goes on.
   Its permission rows (`token scopes`, `label <VERI_PRIORITY_LABEL's value>`, `label bug`,
   `actions read`, `run-state ignore`, `push dry-run`, `bypassPermissions`, the last a paid Haiku
   call) are paid once per clone: pass `--no-permissions` too, and print
   `permission rows skipped: checked <date>` (the date as the file holds it), when
   `.tdd/permissions-checked` in the main working tree holds the current gh login (`gh api user`'s
   `login`), a sha256 of `origin`'s current URL (`git remote get-url origin`; the URL itself, which
   may carry a credential, is never written) and the check's current version,
   and `VERI_RECHECK_PERMISSIONS` is unset or `0`. A missing or stale record — one naming another
   login, URL or version, or one that cannot be read, is malformed or is dated in the future — or
   `VERI_RECHECK_PERMISSIONS=1` runs the permission rows. The record (those three facts and the date)
   is written only after a check that ran them in which every permission row was printed and none
   failed; after one in which any failed, an existing record is left as it was. A record that cannot
   be written costs only the record: one stderr line names it and why, and the run goes on. A
   `VERI_RECHECK_PERMISSIONS` other than `0` or `1`, set-but-empty included, stops the run before
   `ready-check.sh` (`stopped at 2 VERI_RECHECK_PERMISSIONS`, exit 2).
3. **Suite is green at baseline — and time it — on the commit the cycles build on.** Enter
   the issue's worktree first, as step 1.2 describes — slug from the title — and clear any stale stop request there before anything else. The
   worktree's lock, `.tdd/conductor.pid`, is not yours to write: `run_conductor.py` claims it
   with its own pid and start time before this preflight runs (the forked `claude -p` child's
   `record_pid` then writes the child's own pid and start time, and on exit the file is removed
   only when it still names this conductor), and refuses the launch instead (exit 2,
   `already live (pid <pid>)` on stderr, the pid file unchanged, before it writes any run
   record or runs preflight) when the file already names a live process started at the time it
   records (or with no time recorded); a file naming a dead pid is taken over. The conductor itself never writes it, and
   the lock is taken here in step 3, never in step 1.2:
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
   unchanged.
   A run that `issue-worktree.sh` handed back an existing worktree — which it marks by leaving
   the file `.tdd/handed-back` in that worktree; a freshly cut worktree has no such file, and
   whether the ledger `.tdd/issue-<n>.md` exists does not matter — first
   discards whatever a killed leaf left uncommitted, since a rebase refuses a dirty tree:
   ```
   stray="$($S/resume-clean.sh)"
   ```
   `resume-clean.sh` captures `git status --porcelain` and runs `git reset --hard HEAD`, so its
   stdout is the paths that reset discarded: keep it as `$stray` for sub-step 4 to
   name (`<base directory>/RESUME.md`). When `preflight.sh` ran this call, `$stray` is the paths on
   its `stray=` lines.
   When a ledger exists, the script also reconciles it: a tick is committed with its step's green commit, so the committed ledger's ticks record which greens exist, and a working-copy `- [x]` line is kept ticked only when the committed
   ledger holds a tick of the same step text (the text without its trailing markers), so n committed ticks of a text keep at
   most n working ticks of it; every other `- [x]` line — its green commit is not on the branch — is unticked and loses its
   `⟂ refactor pending` mark, and every other working-copy line is kept as written.
   Then the handed-back run, its uncommitted `.tdd/` appends kept
   and its ledger ticks reconciled when a ledger exists, runs
   `$S/rebase-onto-default.sh` before its baseline, so the baseline runs on the rebased tip.
   On an exit 0 the first stdout line of `rebase-onto-default.sh` is `<pre-rebase-sha>`, the HEAD
   the branch held before the rebase (`preflight.sh`'s `rebased_from=` line when it ran the rebase). An exit 3 — the branch already contains `origin/<default>` — goes on unchanged. An exit 1 —
   the rebase conflicted and was aborted, HEAD untouched — goes on from the old base and
   leaves the conflict to the Draft PR step's `develop-rebase` path.
   An exit 0 moved the branch, and is marked in the run log as its own event,
   `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh resume-rebase from=<pre-rebase-sha> rebased="$(git rev-parse HEAD)"`,
   a name nothing the Draft PR step's rebase records shares.
   After that event, and before the baseline, run
   `$S/tests-frozen.sh rerecord-rebased .tdd/issue-<n>.md <pre-rebase-sha>`. Exit 0 or 3 goes on.
   Only a run on a freshly cut worktree skips both the discard and the rebase here.
   Every run below happens in it, so the baseline proves the commit the branch is cut from —
   the freshly fetched `origin/<default>` for a new branch, the branch head on a resume — not
   whatever the caller's checkout has checked out.
   The issue may name its own test command,
   so read its body first — into a temp file, since the worktree must stay clean:
   ```
   body="$(mktemp)" && gh api repos/{owner}/{repo}/issues/<n> -q .body > "$body"
   ```
   Then, before any leaf is launched, check the issue's requirements:
   `$S/requirements-preflight.sh "$body" [<ledger>]`, passing the ledger `.tdd/issue-<n>.md`
   when it exists (as on a resume). It checks every row of every `### <path>` table in the
   issue's `## Requirements` against that unit's `REQUIREMENTS.md` list, and each `⟦skill-edit⟧`
   step's unit against the issue's `### <path>` tables. **Exit 2** is a preflight refusal: it
   names every defect at once, so fix them together. Like every other preflight refusal, it
   sends the run to `<base directory>/PREFLIGHT-FAILURES.md`: `Read` it then and not before,
   and run it. On a fresh run the ledger does not exist
   yet, so `scope-check.sh` checks the skill-edit units at the plan commit instead.
   **On a resume, mark the baseline run as stage `baseline`**, as `preflight.sh` marks a fresh run's: just
   before the fast tier's `detach-command.sh start`, run `VERI_ISSUE=<n> $S/event.sh stage-start stage=baseline`
   and note the time; once the baseline run has answered (the full tier's last wait, or its reused time, or the
   wait that stopped it), run
   `VERI_ISSUE=<n> $S/event.sh stage-end stage=baseline status=<exit code> secs=<seconds>`, whatever its exit: `<exit code>` is the baseline run's exit code (0 when both tiers passed or
   the full tier's time was reused, else the code of the wait that stopped it) and `<seconds>` the whole seconds
   since the start. A red baseline is so counted as failed, never missing; a wait answering 3 is not an exit,
   so wait again first.
   Then, for `detach-command.sh`, get the fast tier's command from `$S/detect-test-command.sh --tier fast --issue "$body" --at <base>` (see *Detecting the test command*), `<base>` the run's recorded branch base: a fresh launch writes `git merge-base HEAD origin/HEAD` (`origin/<stack>` when the cut recorded a stack), read once the worktree is cut, to `.tdd/issue-<n>-branch-base` in the main working tree, stopping with exit 2 before writing when that merge base cannot be read; a resume reads it back from there (else the copy origin's `refs/veri/runs/<n>` carries) and never recomputes it, stopping with exit 2 when it is missing or invalid (not hex, unreadable, not an ancestor of HEAD). `preflight.sh` does both,
   and run it through `$S/detach-command.sh start <name> <cmd>`, then `VERI_ISSUE=<n> $S/detach-command.sh wait <name> --alone '<alone-cmd>'` in the foreground with no max-seconds argument and the Bash tool's `timeout` of 600000 ms, calling `wait` again each time it returns 3 (never background it and end the turn).
   `<alone-cmd>` is the repo's own runner for one test target, with the target as `$1`: a test file, or a pytest node id `path::name` when the red output has `FAILED`/`ERROR` lines (`make test TESTS="$1"` on veri, named here with `detach-command.sh`). With `--alone`, a command that finished red has each failing test its output names re-run alone once, as a pytest node id when it has them and else as a test file, through the shared `rerun_alone` helper: when every one passes alone, `detach-command.sh wait` answers 0 and has itself written the one `suite-flake` event naming the targets, so preflight goes on as on a green baseline.
   `detach-command.sh wait` answers 0 the command passed (or every red test target passed alone), 3 still running (call again).
   A resume whose baseline is red only in suites that are red on the branch head but green on the
   default branch is the exception, checked with `suite-red-resume.sh check` (`Read` `<base directory>/RESUME.md`).
   On such a resume `suite-red-resume.sh insert` inserts no `⟦suite-repair⟧` step when the union of
   the units of the consecutive pending `⟦skill-edit⟧` steps from the first unchecked step explains
   the whole red, so the first such step runs first. When every unit the red is explained by has a
   pending `⟦skill-edit⟧` step but a non-skill-edit unchecked step separates them, `insert` likewise
   inserts no `⟦suite-repair⟧` step and exits 2, naming the reorder the plan needs (the skill-edit
   steps moved together); the other `insert` exit codes are unchanged. Reading the body **here**, before the baseline runs, is what
   keeps the baseline and every later leaf on one command: detected after the baseline, the
   issue's line would arrive too late to be the command the baseline proved green. Note how
   long the run took and keep it as `baseline`, the elapsed wall time in whole seconds
   (round up). This measurement is free — the run happens anyway — and it is taken once, so
   a suite that gets slower mid-run does not move the timeout under a leaf.
   Once that baseline is green, a resume rebase that moved the branch is published with
   `$S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, where `<pre-rebase-sha>`
   is the HEAD recorded before `rebase-onto-default.sh` ran. It is never a bare force: the
   pinned lease refuses the push when the remote branch is no longer the commit this run
   rebased from.

   **Then time the full tier too.** Get its command from
   `$S/detect-test-command.sh --tier all --issue "$body"`, run it once through `detach-command.sh` in the same start-then-wait shape as the preflight baseline, its wait too `VERI_ISSUE=<n> $S/detach-command.sh wait <name> --alone '<alone-cmd>'`,
   and keep its elapsed
   wall time in whole seconds (round up) as `full`; step 7 sizes the run's hard timeout from
   that number, not from `baseline`. The full-tier run is the work a leaf actually does — a
   verifier runs this very command and a developer leaf runs the suites covering the files it
   touched — while no leaf runs the fast tier at all, so a timeout timed off the fast one
   bounds work nobody does: that is how #300's green leaf was killed at the 900 s floor
   twice over while it was working. It is timed here, with the same single-measurement rule,
   and costs one full-tier run the Draft PR gate pays for anyway. If it is red but every red
   test target (a failing pytest node id, else a test file) passes when run alone (`--alone`), as for the baseline, it is a flake: a
   `suite-flake` event names the targets, and preflight goes on.

   `VERI_BASELINE_FULL_TIER` takes `reuse`, the default, or `run`. In both modes the fast-tier
   baseline runs, unless it is skipped as already proven green (below). Settle the mode by running
   `$S/baseline-full-tier.sh <n> <full-tier-command>` and follow its output: `reuse <seconds>`
   means `full` is that many seconds (taken from `$S/full-tier-time.sh`, which holds a time for
   this run's full-tier command recorded no more than `VERI_FULL_TIER_MAX_AGE_DAYS` days ago,
   default 7) and the full tier is not run; `run` means the full tier runs, as above, including
   when `reuse` had no usable time: none, one older than that, or one with no recorded age
   (`.tdd/full-tier-time-at.json`) is not reused. A green full-tier run records its elapsed
   whole seconds and their time through `$S/full-tier-time.sh`, so a later run can reuse it.

   **A baseline already proven green is skipped.** Just before the fast tier would start, two sources are
   asked, and the baseline (the fast tier, and the full tier with it) is skipped when either says green:
   (1) a record on this machine: `$S/baseline-full-tier.sh --green <n> <tree> <fast-cmd> <full-cmd>` prints `skip`
   when `.tdd/baseline-green.json` in the main checkout holds a green baseline keyed by the tree under test
   (`git rev-parse HEAD^{tree}`), both commands, the run's skill commit pin `.tdd/issue-<n>-skill-commit` and a sha256 of
   the dev venv lock `requirements-dev.txt`; (2) CI: `gh run list --workflow CI --event push --commit <sha>`, whose latest run
   is a `push` run, `completed` with conclusion `success` on exactly the commit being baselined (`git rev-parse HEAD`, a fresh launch's
   `origin/<default>` tip). A `pull_request` run never counts: it reports the PR head's sha but tests the merge commit
   with its base, so a resumed PR whose base moved would skip on a tree CI never ran. The record is asked first, so a resume whose branch tip CI never ran is covered by it.
   Fail closed: a CI run that is red, pending, absent or not a `push` run, a `gh` call that fails or prints what cannot be read, a run on
   any other sha (local commits on top, or a rebase), and a record that is absent, corrupt, not green or keyed differently
   each leave the baseline to run. Only a baseline that ran green writes a record, through
   `$S/baseline-full-tier.sh --record-green` with the same arguments; a red one, or one skipped on either source's word, never does, even
   when a later call waits its full tier to green: the record needs a fast tier this preflight ran green.
   A skipped baseline counts as green with `baseline` 0 seconds; `full` still comes from `baseline-full-tier.sh <n>
   <full-tier-command>`, so a full tier with no reusable time is still run once to time it.
   **The trade-off, accepted by the owner:** CI runs on Linux and this machine is a Mac, so a test that fails only
   locally can slip past the CI source. It is bounded to the exact sha CI ran; a tip CI never ran gets the local record,
   which only this machine's own green run writes, or a real baseline.
4. **Default branch.** Capture it for the PR base:
   `gh api repos/{owner}/{repo} -q .default_branch`.
5. **Tunables parse.** Run `$S/refactor-budget.sh 0` once. `VERI_REFACTOR_BUDGET`
   must be a whole number ≥ 0: a budget that cannot be read is a poisoned baseline like a red suite, not a
   decision, and catching it here is what lets the refactor loop treat exit 2 as impossible.
   Exit 0 and exit 3 both mean it parses (3 only says the budget is 0 — a run with the
   refactor loop switched off), so continue.

   Then run `$S/refactor-budget.sh --issue 0` once, which reads `VERI_ISSUE_REFACTOR_BUDGET`,
   the structural pass's budget, the same way: exit 0 and exit 3 both mean it parses.

   Then the plan-growth budget, `VERI_STEP_GROWTH_PERCENT`, which `add-ledger-step.sh` and
   `ledger-growth.sh` read the same way: it must be unset (50), or a whole number ≥ 0. There is
   nothing to run, since that script refuses an anchor it cannot find before it ever looks at
   the budget, so read the value here:
   ```
   [[ -z "${VERI_STEP_GROWTH_PERCENT+x}" || "$VERI_STEP_GROWTH_PERCENT" =~ ^[0-9]+$ ]]
   ```
   Anything else is false, **including set-but-empty** (`stopped at 5 VERI_STEP_GROWTH_PERCENT`).
   The old absolute knob, `VERI_STEP_GROWTH`, is retired and must be unset: any value, empty
   included, is false (`stopped at 5 VERI_STEP_GROWTH`), and the output names
   `VERI_STEP_GROWTH_PERCENT`, since a count set for the old knob would otherwise be silently
   ignored. Caught here
   it costs nothing; left to the first leaf that tries to grow the plan, it surfaces as a
   refused insertion mid-cycle, with the branch, the worktree and the plan already built.

   Then the missing-reroute budget, which `wrong-test-route.sh` reads: it must be unset, or a
   whole number ≥ 0 (unset means 3):
   ```
   [[ "${VERI_MISSING_REROUTE_BUDGET:-3}" =~ ^[0-9]+$ ]]
   ```
   It is a seventh budget axis, never folded into `REVISE_BUDGET`,
   `VERI_STUCK_RETRIES`, `VERI_NO_VERDICT_RETRIES`, `VERI_REFACTOR_BUDGET`, `VERI_STEP_GROWTH_PERCENT` or
   `VERI_SKILL_EDIT_BUDGET`.

   Then `VERI_QUALITY_REPAIRS`, the `⟦quality-repair⟧` steps one ledger may hold (default 1): it must be unset,
   or a whole number ≥ 0:
   ```
   [[ "${VERI_QUALITY_REPAIRS-1}" =~ ^[0-9]+$ ]]
   ```
   Anything else is false, set-but-empty included (`stopped at 5 VERI_QUALITY_REPAIRS`, exit 2), before the baseline.

   Then `VERI_SKIP_VERIFY`: it is a comma-separated list of phases whose verify is skipped. Each
   word must be a phase this release can skip, and `plan` is never one; `branch` is among the phases
   it may name. Any other word is false, before the baseline.

   Then `VERI_BRANCH_REPAIRS`, the repair steps `verify-branch` may append per run (default 1): it must
   be unset, or a whole number ≥ 0. A bad value is exit 2, before the baseline. It is a twelfth budget
   axis, never folded into the other eleven: a rejected branch is not a stuck leaf or a missing verdict.
   ```
   [[ "${VERI_BRANCH_REPAIRS:-1}" =~ ^[0-9]+$ ]]
   ```

   Then `VERI_EFFORT_VERIFIER`, the effort every verifier leaf is launched at: it must be unset, empty, or one of
   `low`, `medium`, `high`, `xhigh` or `max`:
   ```
   [[ -z "${VERI_EFFORT_VERIFIER:-}" || "$VERI_EFFORT_VERIFIER" =~ ^(low|medium|high|xhigh|max)$ ]]
   ```
   Anything else is false (`stopped at 5 VERI_EFFORT_VERIFIER`, exit 2): the CLI ignores an unknown effort with
   only a warning, so a mistyped value would run every verifier at the default.

   Then the two money budgets: run `$S/step-budget.sh` once, with no arguments. `VERI_STEP_BUDGET` and
   `VERI_RUN_BUDGET` must be non-negative decimal numbers, checked before any leaf is launched. Exit 0 prints the step budget,
   then the run budget, one per line.

   Then the adjudication budget: run `$S/adjudicate.sh --check-budget` once, which reads
   `${VERI_ADJUDICATE_BUDGET:-2}`, a non-negative whole number. Exit 0 means it parses; exit 2, its
   stderr naming `VERI_ADJUDICATE_BUDGET`, is a refusal before the baseline, like a bad
   `VERI_REFACTOR_BUDGET`. It is an eighth budget axis, never folded into `REVISE_BUDGET`,
   `VERI_STUCK_RETRIES`, `VERI_NO_VERDICT_RETRIES`, `VERI_REFACTOR_BUDGET`, `VERI_STEP_GROWTH_PERCENT`,
   `VERI_SKILL_EDIT_BUDGET` or `VERI_MISSING_REROUTE_BUDGET`.
6. **Leaf models parse.** Run `$S/leaf-model.sh develop-red`,
   `$S/leaf-model.sh revise-green` and `$S/leaf-model.sh verify-green` once each. All three,
   because the four variables do not all reach every name: `VERI_MODEL_DEVELOPER` is only
   ever read for a developer name, `VERI_MODEL_REVISE` only for a revise one and
   `VERI_MODEL_VERIFIER` only for a verifier one, so a preflight that skipped a name would
   let that name's bad value through and kill every leaf it governs at launch.
   A variable that is empty or whitespace-only is treated as unset, so it never stops the run.
   A value with whitespace in it (`sonnet 5`, `" sonnet"`, `"sonnet "`) cannot be a
   model name — `sonnet 5` is two words where the CLI takes one. The resolver is
   otherwise first called at launch, by which time the branch, the worktree and the plan
   already exist and a typo costs a bail to undo. Exit 0 means continue.
7. **Size the run's hard timeout from the full-tier measurement.** Hand step 3's `baseline`
   and its `full` measurement to `$S/leaf-timeout.sh`, so every leaf of the run is launched
   under the result rather than under the supervisor's fixed 900 s default:
   ```
   timeout="$($S/leaf-timeout.sh "$baseline" --full "$full")"            # step 3 ran the full tier
   timeout="$($S/leaf-timeout.sh "$baseline" --full "$full" --reused)"   # step 3 reused its time
   ```
   `--full` says which of the two measurements the timeout is sized from: the full-tier one
   displaces the fast one rather than mixing with it, because a leaf runs the full tier and
   never the fast one.
   The script keeps a quick suite on today's 900 s and gives a slow one 6 × its baseline —
   which is what stops a leaf whose own test command takes minutes being killed as stuck
   while it is working (#71: a 900 s cap against a 140-250 s suite, two bails, both steps
   reverted). A skipped baseline hands it `0`, never the seconds the skip took. A full tier step 3
   ran still sizes the run; when step 3 reused the full-tier time instead, the call ends in `--reused`
   and the script sizes the run from the full tier's idle duration `make ceiling` records (the
   `idle all <seconds>` line of `VERI_TEST_CEILING_FILE`, default `~/.veri-test-ceiling`); with none
   recorded it keeps 900 s and names that fallback on stderr (#4835: a 1 s skip pinned 900 s
   against probes needing more).
   An export would not survive: every Bash call is a fresh shell. So step 1.2,
   once it has entered the issue's worktree, calls the script again with the issue number,
   which records the settled number once per issue in `.tdd/issue-<n>-timeout` at the run
   worktree's root, and `supervise.sh` reads that file whenever `VERI_TIMEOUT` is unset —
   in every phase of every cycle below, and after a resume, without re-measuring; no launch
   line has to pass it. An explicit `VERI_TIMEOUT` is printed back as given, so setting one by hand still
   wins and the liveness axis stays yours. A run whose timeout is garbage kills every leaf it launches, so
   a malformed measurement, or an explicit `VERI_TIMEOUT` that is not a whole number ≥ 1, is a refusal.

