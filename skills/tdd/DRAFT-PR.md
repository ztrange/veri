## 4. Draft PR

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off but the
`⟦full-suite⟧` and `⟦human-owed⟧` lines, which that script skips and no cycle closes: an
unchecked line carrying either does not hold the run back from this step. The full suite
must be green before this step: each time the run enters this step, run `$S/detect-test-command.sh --tier all`'s command via `detach-command.sh` once,
in the same start-then-wait shape as the preflight baseline — the branch's own full-suite gate, since every leaf runs the fast
command, the affected suites, or both. A run that comes back here after a repair step's cycle runs it again. That nothing is left uncommitted and no step is still only
green is not taken on trust here — sub-step 1 asks. Like every step since 1.2, this one runs
**from inside the worktree** — every command below is issued there, so each sees the issue
branch and its commits without any switching.

**Before any red full-run result takes its repair step or its `rebased-tip-red` bail** — the branch's own run here, and the rebased tip's run in sub-step 1 and after `verify-rebase` — run each test file the red output names alone, once, with the repo's own runner (`make test TESTS="<file>"` on veri). A red output that names no file takes today's path, unchanged. When every file passes alone, the red was a flake: write a `suite-flake` event naming the files, treat the run as green, and name the files in the PR body. When any file stays red alone, the red result stands as it is and takes its repair step or its bail.

A red result on that full run does not bail: append a repair step to the ledger, commit it,
and return to step 3, *The cycle loop* — the failing suites are that step's red evidence. The
repair step's text lists every suite the full run left red, each with its first `FAIL -` line;
the develop and verify prompts take that list from the step's text through their templates,
and the conductor never edits a built prompt to add a suite one of them left out. Its
developer adds a unit-tier test when the failure exposes a gap the fast tier missed, and its
verifier judges the fix against the full command, not the fast one.

When every failing case pins prose of one graded unit, the step appended is a `⟦skill-edit⟧` step naming that unit (run from `<base directory>/SKILL-EDIT.md`), not a `⟦suite-repair⟧` step; otherwise it is the `⟦suite-repair⟧` step as before. A red after that step's cycle bails, with no second repair step (`Read` `<base directory>/BAIL.md`).
```
$S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the full-suite failure: <suite> — <its FAIL - line>> ⟦suite-repair⟧'; rc=$?
[ "$rc" != 2 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=step-add-refused classification="$($S/classify-bail.sh step-add-refused)"
[ "$rc" = 1 ] || [ "$rc" = 2 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
[ "$rc" = 1 ] || [ "$rc" = 2 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red full suite (#<n>)"; }
```
That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
The block captures `add-ledger-step.sh`'s exit code: the `step-added` event, the `git add` and the `git commit` run only on exit 0, after the insertion has happened.
**`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`, writing neither the `step-added` nor the `step-start` event** — see `<base directory>/BAIL.md`.
**`add-ledger-step.sh` exit 1 on the `⟦suite-repair⟧` insertion → bail with cause `suite-red`, naming every suite still red**, exactly as the second-red-run bail below does (`Read` `<base directory>/BAIL.md`).

A second red result on the full run after a repair step does **bail** — the repair step is
one more cycle, not a loop — and the bail names every suite still red, not only the first (`Read` `<base directory>/BAIL.md`).
The cap is one `⟦suite-repair⟧` step per run (a resume starts a new run), and `add-ledger-step.sh`,
not the conductor's judgement, decides it: its exit 1 on the insertion above is the whole answer,
and the conductor does not count repair steps in the ledger itself.
```
VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=suite-red classification="$($S/classify-bail.sh suite-red)" suites='<every suite still red>'
```

The branch's own full run comes first, and it, with any `⟦suite-repair⟧` step it adds, has to
finish green before sub-step 1 runs `rebase-onto-default.sh`: the rebased tip's run there is
the extra run a rebase owes under `VERI_REBASED_TIP_SUITE=local`, never a replacement for the branch's own.

When the branch's own full run is green, record its elapsed seconds and its command with
`$S/full-tier-time.sh --record <seconds> '<full-cmd>'`, `<full-cmd>` being the command that run used: the
record replaces the earlier time for that command.

`VERI_REBASED_TIP_SUITE` takes `local`, the default, or `ci`. Under `local` the rebased tip gets a
full test run of its own. Under `ci` it gets none: the regrade block and the pinned-lease push
still run, and the `wait-ci.sh` line on the pushed rebased tip is that tip's full-suite verdict,
its first red appending the `⟦ci-repair⟧` step as any CI red does. A repository with no CI keeps
`local`.

A `⟦full-suite⟧` ledger line is the one step no cycle ticks — `next-unchecked.sh` skips it,
so it is still unchecked here — and this step ticks it, only once the run's last full-suite
run before the PR is readied is green: the rebased tip's run when sub-step 1 rebased the
branch under `VERI_REBASED_TIP_SUITE=local`, this step's own run otherwise, including under `ci`
(ticking after CI would push a new head and cancel the CI run being waited on). Tick each with `tick-ledger.sh`, handed the literal
matcher `'⟦full-suite⟧'` and called again until it exits 3, and without `--refactor-pending`,
so the line carries no refactor-pending mark (it has no refactor loop to clear one); for each
line's `⟦criterion k⟧` tick the issue criterion it finishes (`$S/tick-issue-criterion.sh <n>
"$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`),
and commit the ledger before sub-step 2. A red run ticks nothing: never tick a `⟦full-suite⟧` line after a
red full-suite run, whatever an earlier run said.

With a stop request pending, this step is **not interrupted** and runs to completion: once
`next-unchecked.sh` exits 3 there is no next ledger commit, and what remains launches no leaf
and loses nothing. So no checkpoint runs here — sub-step 4 asks once, clears the request with
`$S/stop-requested.sh --clear` and says so in the final comment. The exception is the repair
step a red full run appends: it launches leaves and ends in a ledger commit like any other
step, so both checkpoints apply to the repair step as they do in step 3.

1. **Ask the two questions that decide whether there is anything fit to push, and refuse to
   go on while either says no** — both from inside the worktree, before a human is asked to
   look:
   ```
   git status --porcelain
   $S/next-pending-refactor.sh < .tdd/issue-<n>.md
   ```
   A non-empty `git status --porcelain` is work no verifier has seen — the transform a
   killed refactor leaf left on disk — and an exit 0 from `next-pending-refactor.sh` is a
   step that is checked but still only green. On either, **do not ready the PR**, and come back
   here only once both questions have gone quiet — an empty status, and
   `next-pending-refactor.sh` exiting 3 — by going to sub-step 2, whose reset runs before its ask and so discards that work whatever the ask answers: now `Read`
   sub-step 2 of `<base directory>/RESUME.md`. For a pending step sub-step 2 also
   re-enters that step's refactor loop. With **no step pending and none unchecked** the
   reset is the whole remedy: sub-steps 2 and 3 both exit 3, sub-step 4's `### ▶️ Resuming`
   comment (`comment.sh resuming --note-file`) names the paths the reset discarded, and the run comes back here and readies the
   PR — refusing the same tree for ever is not an outcome, discarding it loudly is.
   Once both have gone quiet, bring the branch up to the default one, which may have moved
   while the run worked:
   ```
   $S/rebase-onto-default.sh
   ```
   `rebase-onto-default.sh`'s exit code decides the next action, so nothing after it — the
   rebased tip's full test run in particular — is started until it has returned, and never in
   the same message as the rebase.
   An exit 3 from `rebase-onto-default.sh` — the branch already contains `origin/<default>` —
   continues unchanged to sub-step 2. An exit 2 from `rebase-onto-default.sh` — no answer
   could be obtained, such as an origin that cannot be fetched — does **bail**, as a
   **system** failure (`no-verdict`), with the PR left a draft (`Read` `<base directory>/BAIL.md`). An exit 0 — the branch was
   behind and the rebase applied cleanly — has changed the tree, and the first line it
   printed is `<pre-rebase-sha>`, the sha the branch held before the rebase. The rebased tip
   is a tree no suite has run on, and two green branches can combine into a red one, so first run
   the regrade block below on it, which re-signs a `GRADED` line the rebase alone made stale. Under
   `VERI_REBASED_TIP_SUITE=local` then run
   the full test command (`$S/detect-test-command.sh --tier all`'s, via `detach-command.sh`) once on the rebased tip,
   in the same start-then-wait shape as the preflight baseline, and read its exit code from `wait`;
   under `ci` run no full test command on the rebased tip, and go on to the push below.
   Under `local`, a red result on the rebased tip does not reset and bail outright: write `<red-file>`
   as for any red full run and run `$S/suite-red-resume.sh rebased-tip .tdd/issue-<n>.md <red-file> <pre-rebase-sha>`.
   Its exit 0 keeps the rebased branch, appends one `⟦suite-repair⟧` step naming every red suite, and the
   conductor commits the ledger with `.tdd/issue-<n>-added.md` (`git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md`)
   and returns to step 3, *The cycle loop*, for that repair step; the recorded `.tdd/rebase-lease` carries
   `<pre-rebase-sha>` to the later pinned-lease push. Only its exit 1 (the insertion exits 1; the script has already run
   `git reset --hard <pre-rebase-sha>`, so the bail's push is a fast-forward and the un-rebased branch is what is kept)
   does **bail**, as a **process** failure (`rebased-tip-red`), with the PR left a draft: it is never readied
   (`Read` `<base directory>/BAIL.md`). Its exit 2, no answer, does **bail** as a **system** failure (`no-verdict`,
   `Read` `<base directory>/BAIL.md`). On green, publish the rewritten history:

       $S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>

   The lease is pinned to `<pre-rebase-sha>`, so a remote copy another writer moved in the
   meantime is refused rather than clobbered. Never a bare force, which replaces the remote
   copy whatever is there.

   An exit 1 from `rebase-onto-default.sh` — the rebase conflicted and was aborted, so HEAD
   is back where it stood with a clean tree — prints the conflicting files, one per line.
   Resolving them writes new code no verifier has seen, so a `develop-rebase` leaf does it,
   launched **through the supervisor** like every other, and a blind `verify-rebase` judges
   the resolution before the PR is readied:
   ```
   git rev-parse origin/<default>   # → <onto-sha>
   git rev-parse HEAD               # → <pre-rebase-sha>
   $S/build-develop-prompt.sh rebase .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' <onto-sha> <pre-rebase-sha> "<conflicting-files>" > .tdd/develop-rebase.prompt
   rm -f .tdd/develop-rebase.exit .tdd/develop-rebase.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-rebase $S/run-leaf.sh .tdd/develop-rebase.prompt --permission-mode bypassPermissions > .tdd/develop-rebase.out 2> .tdd/develop-rebase.err
   $S/wait-leaf.sh develop-rebase   # foreground; on exit 3 call it again
   ```
   Once the `develop-rebase` leaf has resolved the conflict, run the regrade block below
   **before** `verify-rebase` is launched, so the verifier judges a tip whose `GRADED` lines are
   current. A stale `GRADED` line from the rebase is no defect of the resolution: it spends no
   `revise` mark and no `REVISE_BUDGET` attempt. Then launch the verifier:
   ```
   rm -f .tdd/verdict-rebase.exit .tdd/verdict-rebase.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-rebase $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" rebase .tdd/issue-<n>-spec.md <onto-sha> <pre-rebase-sha> > .tdd/verify-rebase.reason 2> .tdd/verify-rebase.err
   $S/wait-leaf.sh verdict-rebase   # foreground; on exit 3 call it again
   ```
   A verify-rebase `REJECT` goes round the revise loop with phase `rebase`, within
   `REVISE_BUDGET` like any other phase (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). A malformed verdict does **bail** as a **system**
   failure (`no-verdict`, see `<base directory>/BAIL.md`).
   Only on a verify-rebase `PASS` does the run go on to ready the PR, and first as on exit 0: under `ci` the push under the lease pinned to `<pre-rebase-sha>` with no full test command before it, and under `VERI_REBASED_TIP_SUITE=local` the full test command once on the rebased tip (the regrade having already run before `verify-rebase`), a red result taking `$S/suite-red-resume.sh rebased-tip .tdd/issue-<n>.md <red-file> <pre-rebase-sha>`
   as above (its exit 0 appends the `⟦suite-repair⟧` step and returns to step 3; only its exit 1, after its own
   `git reset --hard <pre-rebase-sha>`, bails `rebased-tip-red`; its exit 2 bails `no-verdict`), and on green the push under
   the lease pinned to `<pre-rebase-sha>` (see `<base directory>/BAIL.md`).

   A rebase not resolved within budget — the leaf reports `REBASE: FAILED` or exits 1 or 2,
   a killed leaf among them, or `REVISE_BUDGET` runs out on verify-rebase `REJECT`s — has
   left a resolution no verifier passed on the branch, so first put the branch back where it
   stood:
   ```
   git reset --hard <pre-rebase-sha>
   ```
   The branch is left un-rebased, and the run does **bail** with cause `rebase-unresolved`, a **process** failure, with the PR left a draft, its
   bail comment naming every conflicting file `rebase-onto-default.sh` printed, so the human it hands the conflict to knows where it is (`Read` `<base directory>/BAIL.md`).

   The regrade runs after the run's last rebase and before the full suite runs on the rebased tip, so a `GRADED` line made stale only by the rebase never turns that suite red; with no rebase it runs here, before the PR is readied. It regrades every unit the run signed with `grade-prose.sh` (a unit whose `GRADED` line the branch adds since `git merge-base HEAD origin/<default>`, in a `GRADED` file at any depth of the tree, the repository root's included), and reads the block's exit: exit 1 (a REJECT) is handled as a red full suite is, by appending a repair step through that same block, so a refused insertion (exit 2) is followed by the `step-add-refused` bail and by no `step-added` or `step-start` event; exit 2 (no verdict could be obtained) is a system-failure bail with cause `no-verdict`, never a repair step (see `<base directory>/BAIL.md`). Once a unit's text has been REJECTed, a regrade of the same text (the same signature input) may not re-sign it: only an author run that changes the text, followed by a PASS, may. Once that repair step's cycle closes, the run comes back to this Draft PR step and runs the full suite again, then the rebase and the regrade, as it does after a `⟦suite-repair⟧` step.
   ```
   base=$(git merge-base HEAD origin/<default>)
   git diff "$base" HEAD -U0 -- ':(glob)**/GRADED' | sed -n 's/^+\([^+][^ ]*\) .*/\1/p' | { rc=0; while read -r unit; do
     $S/grade-prose.sh "$(dirname "$unit")/REQUIREMENTS.md" "$unit" </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
   done
   $S/grade-prose.sh --convert </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
   exit "$rc"; }
   ```
   After the units the run signed, the block runs `$S/grade-prose.sh --convert` on the tree, so a unit the default branch signed under a formula the branch replaces is re-signed under the tree's before the rebased tip's full suite; its exit is folded into the block's highest exit code.

   Run `$S/refactor-owed.sh list .tdd/issue-<n>-refactor-owed.md` once, before the PR is readied.
   When it prints a candidate (exit 0), then and not before, run the issue's one structural pass:
   `Read` and run `<base directory>/STRUCTURAL.md`. On exit 3 the run never reads it.
   No candidate — `list` exits 3, and a missing `.tdd/issue-<n>-refactor-owed.md` is the
   `list` exit-3 case — skips the pass with no bail: it is marked `stopped=nothing-structural`
   before the PR is readied:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh structural-pass stopped=nothing-structural
   ```
   Right after the structural pass (or this skip) and before the PR is readied, run
   `$S/refactor-candidates.sh <n> .tdd/issue-<n>-refactor-owed.md` once. Exit **0** prints the
   candidates issue's url, which goes in the PR body's `## Refactor owed` section; exit **3**
   (nothing out-of-bounds or not done) does nothing; exit **2** is a system failure: **bail**
   with cause `no-verdict` (`Read` `<base directory>/BAIL.md`). The candidates issue is never
   labelled with the opt-in label (`VERI_LABEL`) and is filed at most once per run: a resume
   runs the same command and it replaces the existing issue's body.
2. **Mark the PR ready for review and read its CI, then close the run's log with the PR's
   URL, render the metrics, commit them, and rewrite the PR into its final form** — one
   sub-step, in this order, from inside the worktree. **This step opens no PR.** Step 2.3 opened it at the plan commit, so
   there is nothing left here for a PR-creating `gh api` call to do: a second one against a branch that
   already has an open PR is either a refusal that ends the run at its last step, or a second
   PR for the same branch — and then the claim another machine reads and the page a human is
   asked to merge are two different pages. Read the existing PR's URL rather than assuming the
   run remembers it, so a resumed run edits the PR its branch already has:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   blocked=; $S/pr-ready.sh <pr-number> "$(git rev-parse HEAD)" 2> .tdd/pr-ready.err || { blocked=1; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=pr-ready-failed classification="$($S/classify-bail.sh pr-ready-failed)"; }
   [ -n "$blocked" ] || $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" > .tdd/wait-ci.out 2> .tdd/wait-ci.err; ci=$?    # exit 3 → run this line again, in a new Bash call
   grep -F 'conflicts with its base branch' .tdd/wait-ci.err > /dev/null; conflict=$?
   # A `wait-ci.sh` exit 2 naming no conflict is adjudicated first, before the `ci-timeout` bail event (`Read` `<base directory>/ADJUDICATE.md`): a `retry` runs `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"` and then the same `wait-ci.sh` line once more, its exits handled as at the first wait; any other outcome, or a spent budget, writes the `ci-timeout` bail that follows.
   [ "$ci" != 2 ] || [ "$conflict" = 0 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"
   graded=1; [ "$ci" != 2 ] || [ "$conflict" != 0 ] || { $S/rebase-onto-default.sh --graded-only > .tdd/graded-rebase.out; graded=$?; }
   [ "$ci" != 2 ] || [ "$conflict" != 0 ] || [ "$graded" = 0 ] || [ ! -e .tdd/ci-conflict-rebased ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"
   [ "$ci" != 1 ] || gh run view <run-id> --log-failed          # a failed check only → its suite and FAIL - line
   [ "$ci" != 1 ] || ! $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(cat .tdd/wait-ci.out)"
   [ "$ci" = 0 ] || [ "$ci" = 2 ] || $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null; no_repair=$?
   [ "$no_repair" = 0 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
   [ "$no_repair" = 0 ] || $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the CI failure: <suite> — <its FAIL - line>> ⟦ci-repair⟧'
   [ "$no_repair" = 0 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red CI check (#<n>)"; }
   ```
   That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
   **`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
   When `pr-ready.sh` exits non-zero, its stderr is kept in `.tdd/pr-ready.err` and the block writes exactly one event, the `pr-ready-failed` bail, and nothing else: `blocked` makes the wait line skip `wait-ci.sh` and leave `ci` at 0, so no CI deadline is started, no `ci-timeout`, `ci-conflict` or `ci-red` bail follows, no `step-added` event, `⟦ci-repair⟧` ledger line or `plan: repair the red CI check` commit is made and no `gh run view` is asked for. The run **bails** as a **system** failure (`pr-ready-failed`, classified by `classify-bail.sh`) with the PR left a draft, the bail comment carrying the text of `.tdd/pr-ready.err` as its last reason (`Read` `<base directory>/BAIL.md`).
   A `ci-timeout` or `ci-red` bail ends the step there, and neither the `done` mark nor the
   `metrics:` commit below follows it (`Read` `<base directory>/BAIL.md`). Otherwise:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>
   $S/metrics.sh <n> > .tdd/issue-<n>-metrics.md; metrics=$?
   if [ "$metrics" = 0 ]; then
     git add .tdd/issue-<n>-metrics.md
     git commit -m "metrics: what solving #<n> cost (#<n>)"
   fi
   $S/push-branch.sh
   $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" > .tdd/wait-ci.out 2> .tdd/wait-ci.err; ci=$?    # exit 3 → run this line again, in a new Bash call
   [ "$ci" != 1 ] || ! $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(cat .tdd/wait-ci.out)"
   [ "$ci" = 0 ] || [ "$ci" = 2 ] || $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null; no_repair=$?
   [ "$no_repair" = 0 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
   [ "$no_repair" = 0 ] || $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the CI failure: <suite> — <its FAIL - line>> ⟦ci-repair⟧'
   [ "$no_repair" = 0 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red CI check (#<n>)"; }
   grep -F 'conflicts with its base branch' .tdd/wait-ci.err > /dev/null; conflict=$?
   # A `wait-ci.sh` exit 2 naming no conflict is adjudicated first, before the `ci-timeout` bail event (`Read` `<base directory>/ADJUDICATE.md`): a `retry` runs `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"` and then the same `wait-ci.sh` line once more, its exits handled as at the first wait; any other outcome, or a spent budget, writes the `ci-timeout` bail that follows.
   [ "$ci" != 2 ] || [ "$conflict" = 0 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"
   graded=1; [ "$ci" != 2 ] || [ "$conflict" != 0 ] || { $S/rebase-onto-default.sh --graded-only > .tdd/graded-rebase.out; graded=$?; }
   [ "$ci" != 2 ] || [ "$conflict" != 0 ] || [ "$graded" = 0 ] || [ ! -e .tdd/ci-conflict-rebased ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"
   $S/refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md
   gh api -X PATCH repos/{owner}/{repo}/pulls/<pr-number> -f title="<type>: <criterion summary> (#<n>)"
   cat > .tdd/issue-<n>-pr-body.md <<'EOF'
   <Closes #<n> — summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed; followed by the contents of .tdd/issue-<n>-metrics.md (or, when $metrics is not 0, the line 'metrics could not be rendered: metrics.sh exited $metrics' in its place), followed by that render's output, followed by the ledger's ## Owed steps bullets, followed by the conductor's mutation-parity.sh report as the pairs table, followed by its ⟦human-owed⟧ lines and each row that report owes under ## Owed by a human; and, when .tdd/issue-<n>-skip-verify is non-empty, the line '⚠️ Unverified phases: <list>'>
   EOF
   $S/pr-body.sh <pr-number> .tdd/issue-<n>-pr-body.md
   ```
   **`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
   The title is set by `gh api -X PATCH`, the body by `$S/pr-body.sh <pr-number> <body-file>`, never a whole-body `-f body=…` replacement: `pr-body.sh` keeps every section the run did not author, so a `## Review notes` section appended after the body survives a resumed run's next write.
   The readied PR's CI is read fail-closed, the way the `merge` skill reads it: an empty
   rollup is never a pass, and a completed check whose conclusion is anything other than
   `SUCCESS`, `NEUTRAL` or `SKIPPED` counts as failed. A pending check never counts as
   green, and the wait is `wait-ci.sh`, one bounded slice per Bash call, given the full 40-hex sha just
   pushed (`git rev-parse HEAD`; an abbreviated one exits 2) so a rollup still reporting the previous head reads as pending: its exit 3 means a
   check is still pending, so call it again in a new Bash call; its exit 2 — a check still
   pending past the deadline its first call recorded, checks still queued `VERI_CI_QUEUE_WAIT` seconds after the first call that saw them queued, a ready, mergeable PR whose head has no check run and no commit status for `VERI_CI_NO_RUN_WAIT` seconds (default 600, a non-negative whole number; the grace restarts for each new head) while a `pull_request` workflow exists, its stderr naming `no CI run for <sha>` with the full 40-hex head, or `gh` unable to read the checks until that deadline (a 4xx other than 403 or 429 at once) — does
   **bail**, with cause `ci-timeout`, rather than waiting on (`Read` `<base directory>/BAIL.md`).
   A `wait-ci.sh` exit 2 naming no conflict is adjudicated first, before the `ci-timeout` bail event (`Read` `<base directory>/ADJUDICATE.md`): a `retry` runs `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"` and then the same `wait-ci.sh` line once more, its exits handled as at the first wait; any other outcome, or a spent budget, writes the `ci-timeout` bail below.
   That deadline is `wait-ci.sh`'s own bound, since the call gives no total-seconds: twice the
   mean of the last 5 completed CI runs, capped at 10 minutes, or 540 s when fewer than 5
   exist or `gh` cannot answer.
   A failed check does not bail: read its run's log with `gh run view <run-id> --log-failed`,
   append a repair step to the ledger whose text quotes the failing suite and its `FAIL -`
   line — or the error line, when the suite died before writing one — commit the ledger, and
   return to step 3, *The cycle loop*, without the `done` mark: the quoted line is that
   step's red evidence, the same way a red full run's repair step is.
   A second red CI result after a CI repair step does **bail**, with cause `ci-red`, the way
   a second red full run does — the repair step is one more cycle, not a loop (`Read` `<base directory>/BAIL.md`).
   A conductor never re-runs a failed CI job — no `gh run rerun`, no re-run of a failed
   check: a red check is answered only by the repair step or the `ci-red` bail above, since
   a re-run can turn a real failure into one that reads as a flake. Re-running a known flake
   is the operator's decision, made outside a run.
   That bail keys on `⟦ci-repair⟧` only: a ledger holding a `⟦suite-repair⟧` step and no
   `⟦ci-repair⟧` step still gets its one CI repair attempt.
   A `wait-ci.sh` exit 2 whose stderr names a conflict — the PR conflicts with its base
   branch, so no workflow will start on it — is not a timeout. The conflict is first offered to
   `$S/rebase-onto-default.sh --graded-only`, which resolves a conflict confined to `GRADED` files
   by unit — the branch's line for each unit it signs, the base's line for every other unit — and
   prints `<pre-rebase-sha>` then the onto sha, or aborts and exits non-zero leaving HEAD where it
   stood. Its exit 0 touches no `.tdd/ci-conflict-rebased` and never spends the run's one rebase: it goes on
   with the regrade block, under `VERI_REBASED_TIP_SUITE=local` the full suite once on the rebased tip (under `ci`, none), the push under the lease pinned
   to the printed `<pre-rebase-sha>`, and the same `wait-ci.sh` line, a red rebased tip under `local` taking
   sub-step 1's `rebased-tip-red` bail with its reset (`Read` `<base directory>/BAIL.md`). Its non-zero exit takes the rule unchanged:
   with `.tdd/ci-conflict-rebased` absent, `touch .tdd/ci-conflict-rebased` and rebase onto
   `origin/<default>` once, through the existing rebase path of sub-step 1: `$S/rebase-onto-default.sh`
   (no flag), its `develop-rebase` leaf and rebase verifier (`verify-rebase`) when it conflicts, the
   regrade block, then under `VERI_REBASED_TIP_SUITE=local` the full suite once on the rebased tip (under `ci`, none), and the push under the lease pinned
   to `<pre-rebase-sha>` — then wait for CI again with the same `wait-ci.sh` line; with it present,
   **bail** with cause `ci-conflict`, rather than rebasing again (`Read` `<base directory>/BAIL.md`).
   There too `rebase-onto-default.sh`'s exit code decides the next action, so nothing after it — the
   rebased tip's full test run in particular — is started until it has returned, and never in the
   same message as the rebase. Sub-step 1's own rebase takes no flag and does not change.
   The `metrics:` push starts a CI run of its own on the readied PR, so it is read the same
   way, by `wait-ci.sh` after the push; a red there (exit 1) is a CI-only failure on code
   that was already green, so it appends one `⟦ci-repair⟧` step to the ledger with the same
   `step-added` event a conductor-added step gets, through the same three lines and ledger
   commit as a failed check above, and returns to step 3, *The cycle loop*, to repair it as a
   red full suite is repaired; it bails with cause `ci-red` only when the ledger already holds
   a `⟦ci-repair⟧` step, and exit 2 bails with cause `ci-timeout` (`Read` `<base directory>/BAIL.md`).
   A `wait-ci.sh` exit 2 naming no conflict is adjudicated first, before the `ci-timeout` bail event (`Read` `<base directory>/ADJUDICATE.md`): a `retry` runs `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"` and then the same `wait-ci.sh` line once more, its exits handled as at the first wait; any other outcome, or a spent budget, writes the `ci-timeout` bail below.
   A `wait-ci.sh` exit 2 after the `metrics:` push whose stderr names a conflict takes the same one-rebase path as a conflict at the first CI wait, and bails with cause `ci-conflict` on a second, so the run never waits into `ci-timeout` on it (`Read` `<base directory>/BAIL.md`).
   The `done` mark comes before the render because `metrics.sh` reads it for both the Outcome
   and the issue's wall time: a report rendered before it exists says `unknown` for both. The
   body is rewritten only after the `metrics:` commit is pushed, so it never quotes a file the
   branch does not yet carry. The title drops the `WIP:` prefix step 2.3 opened it with, and
   `gh_pr_ready` (in `veri/github.py`, behind `pr-ready.sh`, never sourced into the conductor's shell) is what turns the run's claim into a review request: a finished run that left
   a draft behind asks nobody to look.
   `<type>` is **`fix`** on a bug run — the issue carries the `bug` label, so the title
   starts with the `fix:` prefix, the same prefix its green commits took — **`refactor`** on
   a refactor-kind run, the issue labelled `refactor`, so the title starts with the
   `refactor:` prefix — and `feat` otherwise. A bug run's PR titled `feat:` announces to the
   human deciding the merge a capability the run did not add, and so does a refactor run's.
   One `metrics:` commit, and the report sits beside the ledger it describes — the
   `issue-<n>-metrics.md` name is already on the keep side of the run-state ignore rule, so
   nothing else has to change for it to be tracked.
   The render is what puts every step's structural leftovers in front of the human who
   decides the merge, rather than leaving them in a committed file nobody is pointed at.
   When it exits 3 — no step left anything structural behind — it prints nothing, and the
   `## Refactor owed` section is **omitted** from the body: a heading over an empty list
   promises a backlog nobody left.
   The ledger's own owed steps are copied the same way, and out of the ledger itself: every
   plain bullet under the trailing `## Owed steps` heading of `.tdd/issue-<n>.md` — a step
   `add-ledger-step.sh` could not fit inside `VERI_STEP_GROWTH`, which nothing in the run
   reads again — goes into the PR body under a `## Owed steps` heading of its own. A ledger
   carrying no such heading adds no such section.
   What a human still owes is copied last: every `⟦human-owed⟧` ledger line — a record of a
   manual check, which no cycle ticks — goes into the PR body under an `## Owed by a human`
   heading, each listed with its criterion number from its `⟦criterion k⟧` mark, so the
   reviewer sees which issue criterion is still waiting on them. A ledger holding no
   `⟦human-owed⟧` line adds no such section.
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Before posting it, run `$S/stop-requested.sh`. Then post the final done comment by running
   `$S/comment.sh <n> done`, composing none of it: it posts `### ✅ Done — <pr-url>` (the url from
   the `done` mark sub-step 2 wrote) with the same `### 📊 Metrics` block under it, verbatim from
   the file just committed — or, when that file is absent or unusable and `metrics.sh` cannot render
   it, the line `metrics could not be rendered: metrics.sh exited <code>` in its place. When
   `.tdd/issue-<n>-skip-verify` is non-empty it adds `⚠️ Unverified phases: <list>`, and when
   `.tdd/stop` exists (the stop request just asked about) it adds the line saying that a stop arrived
   after the last step, so the run finished rather than pausing. It writes a `comment` event and no
   second `done` mark; exit 2 (no `done` mark, or no answer from GitHub) is a system failure: **bail**
   with cause `no-verdict` (`Read` `<base directory>/BAIL.md`). When the earlier
   `$S/stop-requested.sh` exited 0 or 2, run `$S/stop-requested.sh --clear` after the call, so the
   next run is not paused by it; on exit 3 add nothing.

**The worktree stays.** Do not remove it here: it holds the run's leaf logs and is where a
resume would land if the PR comes back for more work. It is removed once the PR is **merged**
— by the `merge` skill's cleanup, or by the human — with
`$S/issue-worktree.sh --remove <n>`, which refuses (exit 2) if anything in it is still
uncommitted rather than destroying it.

Report back to the user with the branch name, the worktree path, and the PR URL — and say
that their own checkout was not switched.

A verifier's `REJECT` does not stop the run: `Read` and run `<base directory>/REVISE.md`. It spends `REVISE_BUDGET` revise attempts, **default 2**, before bailing the step (see `<base directory>/BAIL.md`).

