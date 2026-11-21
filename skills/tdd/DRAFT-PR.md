## 4. Draft PR

On entering this step run `$S/run-pr.sh <n>` first, again on exit 3; at its `title` seam set the title and call it again; at its `body`
seam write the body and go on to sub-step 3; on any other stop go on by the point its last line names. Each stage's call line below stays.

At the first stage, run `$S/branch-gate.sh <n>` first, again on exit 3; on exit 0 take `branch_suite=` from its last lines
(under `local` the branch's full run below is made green and its time recorded, and no `⟦full-suite⟧` line is ticked);
on any other exit go on by the paragraphs below from the point its last line names.

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off but the
`⟦full-suite⟧` and `⟦human-owed⟧` lines, which that script skips and no cycle closes: an
unchecked line carrying either does not hold the run back from this step. Each time the run enters this step, first settle
whether CI stands in for the branch's own full run: run `$S/branch-suite.sh` at the root of this run's worktree and follow its output. Unset,
`VERI_BRANCH_SUITE` makes it print `ci` when a workflow under `.github/workflows/` triggers on pull requests and `local` otherwise
(`VERI_CI_ON_PR`, when set, answers that in the tree's place, or when it is unset the target `CLAUDE.md`'s `veri: ci on pr:` line); an explicit `ci` or `local` is printed as given. Wherever this step says
"under `VERI_BRANCH_SUITE=local`" or "under `VERI_BRANCH_SUITE=ci`", the mode is the one that script printed, never the environment read directly.
Under `VERI_BRANCH_SUITE=ci` the branch gets no local full run here and no `full-tier-time.sh` record: go on to sub-step 1, and the first
`wait-ci.sh` of sub-step 2 is the branch's full-suite verdict, its first red appending the `⟦ci-repair⟧` step as any CI red does; a run that
comes back here after that step's cycle makes no local full run either. Under `VERI_BRANCH_SUITE=local` the two sentences that follow apply. The full suite
must be green before this step: each time the run enters this step, run `$S/detect-test-command.sh --tier all`'s command via `$S/detach-command.sh` once,
in the same start-then-wait shape as the preflight baseline — the branch's own full-suite gate, since every leaf runs the fast
command, the test files covering the files its step changed, or both, and none runs a broader tier. A run that comes back here after a repair step's cycle runs it again. Each such run is
stage `full-suite`: `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh stage-start stage=full-suite` just before it starts, and
once its result is in, whatever it is, `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh stage-end stage=full-suite status=<exit code> secs=<seconds>`,
`<exit code>` the run's own (never a wait's 3) and `<seconds>` the whole seconds from that start to the result. Under
`VERI_BRANCH_SUITE=ci` no run is made here, so neither line is written. That nothing is left uncommitted and no step is still only
green is not taken on trust here — sub-step 1 asks. Like every step since 1.2, this one runs
**from inside the worktree** — every command below is issued there, so each sees the issue
branch and its commits without any switching.

**A stacked run.** Each time the run enters this step, first settle whether the run is stacked, in two
Bash calls of their own:
1. `test -f .tdd/issue-<n>-base` (the base `issue-worktree.sh` recorded when it cut the run from a stack). Exit 1:
   the run is not stacked, and every sub-step runs as written. Exit 0: go on to 2.
2. `$S/stack-branch.sh`. Exit 0 printing the name `.tdd/issue-<n>-base` holds: the run is stacked, read below as
   `<stack>`. Exit 0 printing another name, exit 3 or exit 2: **bail** with cause `no-verdict` (`Read`
   `<base directory>/BAIL.md`).

In a stacked run, `origin/<default>` in the step's rebases and in the regrade block's `git merge-base HEAD origin/<default>`
means `origin/<stack>` (`rebase-onto-default.sh` already rebases onto it), so the run's diff never carries joined but
unlanded commits. Sub-step 2 runs neither of its blocks: it runs these lines instead, each in a Bash call of its own, in
this order, none reading a variable another line set. Any exit not named here **bails** with cause `no-verdict`
(`Read` `<base directory>/BAIL.md`).
1. `gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'`: exit 0 printing a url is
   `<pr-url>`, `<pr-number>` its last path segment; printing nothing bails.
2. `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>`: exit 0, go on.
3. `$S/metrics.sh <n> > .tdd/issue-<n>-metrics.md`: exit 0 runs line 4; any other exit `<code>` skips line 4, and
   line 8's body carries `metrics could not be rendered: metrics.sh exited <code>` in the metrics' place.
4. `git add .tdd/issue-<n>-metrics.md && git commit -m "metrics: what solving #<n> cost (#<n>)"`: exit 0, go on.
5. `$S/push-branch.sh`: exit 0, go on.
6. `$S/refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md`: exit 0, its output is the body's `## Refactor owed`
   section; exit 3, the body has no such section. Then, in a Bash call of its own,
   `$S/ledger-growth.sh split .tdd/issue-<n>.md`: its output and exit make the body's `## Plan growth` section as in
   sub-step 2's second block, and no exit of it bails.
7. `gh api -X PATCH repos/{owner}/{repo}/pulls/<pr-number> -f title="<type>: <criterion summary> (#<n>)"`: exit 0,
   go on. It drops the `WIP:` prefix and leaves the pull request a draft: a title PATCH never readies one.
8. Write `.tdd/issue-<n>-pr-body.md` with the body sub-step 2's second block writes.
9. `$S/pr-body.sh <pr-number> .tdd/issue-<n>-pr-body.md`: exit 0, go on to sub-step 3.

So a stacked run runs no `pr-ready.sh` and no `wait-ci.sh`, before or after the `metrics:` push: CI on the stack's tip
is the full suite. It ticks no `⟦full-suite⟧` line, whatever full run it made, makes no `plan: the full suite is
owed to CI` commit and adds no `⟦ci-repair⟧` step, and it ends ✅ Done with its pull request a draft. Every other part
of the step runs as for a run that is not stacked.

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
$S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the full-suite failure: <suite> — <its FAIL - line>> ⟦suite-repair⟧' 2> .tdd/add-ledger-step.err; rc=$?
[ "$rc" != 2 ] || { $S/adjudicate.sh left <n> && { echo "adjudicate step-add-refused"; exit 0; }; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=step-add-refused classification="$($S/classify-bail.sh step-add-refused)"; }
[ "$rc" = 1 ] || [ "$rc" = 2 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
[ "$rc" = 1 ] || [ "$rc" = 2 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red full suite (#<n>)"; }
```
That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
The block captures `add-ledger-step.sh`'s exit code: the `step-added` event, the `git add` and the `git commit` run only on exit 0, after the insertion has happened.
**`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`, writing neither the `step-added` nor the `step-start` event** — see `<base directory>/BAIL.md`. Its stderr is kept in `.tdd/add-ledger-step.err`, and the exit is adjudicated before any `bail` event, in the order `ADJUDICATE.md`'s *Procedure* gives (`Read` `<base directory>/ADJUDICATE.md`): the block's `$S/adjudicate.sh left <n>` runs first, and its exit 3 or 2 writes the bail on that same line; on its exit 0 that line writes nothing and ends the Bash call (`exit 0`, printing `adjudicate step-add-refused`), so no later line of the block runs. Then, in Bash calls of their own, run `$S/build-adjudicate-prompt.sh <n> step-add-refused 2 .tdd/add-ledger-step.err add-ledger-step.sh .tdd/issue-<n>.md after <anchor> <step text> > .tdd/adjudicate-step-add-refused.prompt`, the `adjudicate-step-add-refused` leaf launched through `supervise.sh` and waited on, and `$S/adjudicate.sh record <n> step-add-refused .tdd/adjudicate-step-add-refused.out`; whatever it answers, `retry` included, run, alone in a Bash call of its own, `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=step-add-refused classification="$($S/classify-bail.sh step-add-refused)"`, calling `add-ledger-step.sh` no more and writing neither a `step-added` nor a `step-start` event.
**`add-ledger-step.sh` exit 1 on the `⟦suite-repair⟧` insertion → bail with cause `suite-red`, naming every suite still red**, exactly as the second-red-run bail below does (`Read` `<base directory>/BAIL.md`).

A second red result on the full run after a repair step does **bail** — the repair step is
one more cycle, not a loop — and the bail names every suite still red, not only the first (`Read` `<base directory>/BAIL.md`).
The cap is one `⟦suite-repair⟧` step per run (a resume starts a new run), and `add-ledger-step.sh`,
not the conductor's judgement, decides it: its exit 1 on the insertion above is the whole answer,
and the conductor does not count repair steps in the ledger itself.
```
VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=suite-red classification="$($S/classify-bail.sh suite-red)" suites='<every suite still red>'
```

Under `VERI_BRANCH_SUITE=local` the branch's own full run comes first, and it, with any `⟦suite-repair⟧` step it adds, has to
finish green before sub-step 1 runs `rebase-onto-default.sh`: the rebased tip's run there is
the extra run a rebase owes under `VERI_REBASED_TIP_SUITE=local`, never a replacement for the branch's own.

When the branch's own full run is green, record its elapsed seconds and its command with
`$S/full-tier-time.sh --record <seconds> '<full-cmd>'`, `<full-cmd>` being the command that run used: the
record replaces the earlier time for that command.

`VERI_REBASED_TIP_SUITE` takes `ci` or `local`. Settle the mode by running
`$S/rebased-tip-suite.sh` at the root of this run's worktree and follow its output: unset, it prints `ci` when a
workflow under `.github/workflows/` triggers on pull requests and `local` otherwise (`VERI_CI_ON_PR`,
when set, answers that in the tree's place, or when it is unset the target `CLAUDE.md`'s `veri: ci on pr:` line), so a repository with no CI on its pull requests gets
the local run; an explicit value is printed as given. Wherever this step says "under
`VERI_REBASED_TIP_SUITE=local`" or "under `ci`", the mode is the one that script printed, never the
environment read directly. Under `local` the rebased tip gets a
full test run of its own. Under `ci` it gets none: the regrade block and the pinned-lease push
still run, and the `wait-ci.sh` line on the pushed rebased tip is that tip's full-suite verdict,
its first red appending the `⟦ci-repair⟧` step as any CI red does.

A `⟦full-suite⟧` ledger line is the one step no cycle ticks — `next-unchecked.sh` skips it,
so it is still unchecked here — and this step ticks it. When a local full run was made before the PR is readied, it ticks it only once the run's last full-suite
run before the PR is readied is green: the rebased tip's run when sub-step 1 rebased the
branch under `VERI_REBASED_TIP_SUITE=local`, this step's own run under `VERI_BRANCH_SUITE=local` otherwise, including under `VERI_REBASED_TIP_SUITE=ci`
(a tick pushed on its own after CI would be a new head, cancelling the CI run being waited on). Under `VERI_BRANCH_SUITE=ci`, when no local
full run was made on the head being readied (the branch's own is not run, and sub-step 1 either did not rebase or ran under
`VERI_REBASED_TIP_SUITE=ci`), every unchecked `⟦full-suite⟧` line, and each line's issue criterion, is ticked before `pr-ready.sh`, as
owed to CI, in the way described next, and the ledger is committed as `plan: the full suite is owed to CI (#<n>)` before the `metrics:`
commit, so the one push before readying carries both and no records-only push follows the readied PR. That tick waits for no CI run and
reads no `.tdd/wait-ci.err`, and it is never CI's verdict: CI's verdict on the head stays the proof. A red CI still appends the
`⟦ci-repair⟧` step (or bails `ci-red`), a resumed run still waits on CI for the head, a `wait-ci.sh` exit 0 whose `.tdd/wait-ci.err`
says the PR `has no checks` proves nothing (the PR body says so, as sub-step 2's second block gives), and the merge reads CI on the head
it merges, never the tick. A rebase after the PR was readied (the conflict rebase of sub-step 2) moves no tick: CI on the rebased head is
read as on any head. Tick each with `tick-ledger.sh`, handed the literal
matcher `'⟦full-suite⟧'` and called again until it exits 3, and without `--refactor-pending`,
so the line carries no refactor-pending mark (it has no refactor loop to clear one); for each
line's `⟦criterion k⟧` tick the issue criterion it finishes (`$S/tick-issue-criterion.sh <n>
"$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`),
and commit the ledger before sub-step 2 (under `VERI_BRANCH_SUITE=ci` with no local full run before readying, inside sub-step 2's
first block, before the `metrics:` commit, as said above). A red local run ticks nothing: never tick a `⟦full-suite⟧` line after a
red full-suite run, whatever an earlier run said.

With a stop request pending, this step is **not interrupted** and runs to completion: once
`next-unchecked.sh` exits 3 there is no next step's ledger commit (only this step's own `⟦full-suite⟧` tick), and what remains launches no leaf
and loses nothing. So no checkpoint runs here — sub-step 4 asks once, clears the request with
`$S/stop-requested.sh --clear` and says so in the final comment. The exception is the repair
step a red full run appends: it launches leaves and ends in a ledger commit like any other
step, so both checkpoints apply to the repair step as they do in step 3.

1. Run `$S/pr-prepare.sh <n>` first, again on exit 3. On exit 0 take `rebased`, `rebased_from` and
   `rebased_tip_suite` from its last lines (nothing rebased: `rebased=0`, `rebased_tip_suite=none`) and go on from the lint run
   below, the structural pass skipped; on any other exit go on by this sub-step from the point its last line names.
   **Ask the two questions that decide whether there is anything fit to push, and refuse to
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
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-rebase $S/run-verdict.sh --branch-base <onto-sha> --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" rebase .tdd/issue-<n>-spec.md <onto-sha> <pre-rebase-sha> > .tdd/verify-rebase.reason 2> .tdd/verify-rebase.err
   $S/wait-leaf.sh verdict-rebase   # foreground; on exit 3 call it again
   ```
   A verify-rebase `REJECT` goes round the revise loop with phase `rebase`, within
   `REVISE_BUDGET` like any other phase (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). A malformed verdict does **bail** as a **system**
   failure (`no-verdict`, see `<base directory>/BAIL.md`), and so does `verify.sh`'s exit 2 (through
   `run-verdict.sh`) for a tracked file the leaf left modified and uncommitted (the verifier is never launched; `.tdd/verify-rebase.err` names the
   paths), since the push would ship HEAD without that change.
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

   The regrade runs after the run's last rebase and before the full suite runs on the rebased tip, so a `GRADED` line made stale only by the rebase never turns that suite red; with no rebase it runs here, before the PR is readied. It regrades every unit the run signed with `grade-prose.sh` (a unit whose `GRADED` line the branch adds since `git merge-base HEAD origin/<default>`, in a `GRADED` file at any depth of the tree, the repository root's included, as `$S/grade-prose.sh --signed "$base"` lists it), and reads the block's exit: exit 1 (a REJECT) is handled as a red full suite is, by appending a repair step through that same block, so a refused insertion (exit 2) is followed by the `step-add-refused` bail and by no `step-added` or `step-start` event; exit 2 (no verdict could be obtained) is a system-failure bail with cause `no-verdict`, never a repair step (see `<base directory>/BAIL.md`). Once a unit's text has been REJECTed, a regrade of the same text (the same signature input) may not re-sign it: only an author run that changes the text, followed by a PASS, may. Once that repair step's cycle closes, the run comes back to this Draft PR step and, under `VERI_BRANCH_SUITE=local`, runs the full suite again, then the rebase and the regrade, as it does after a `⟦suite-repair⟧` step.
   ```
   base=$(git merge-base HEAD origin/<default>)
   rc=0; units=$($S/grade-prose.sh --signed "$base" </dev/null) || rc=$?
   printf '%s\n' "$units" | { while IFS="$(printf '\t')" read -r reqs unit; do
     [ -z "$unit" ] || $S/grade-prose.sh "$reqs" "$unit" </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
   done
   $S/grade-prose.sh --convert </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
   exit "$rc"; }
   ```
   The block hands `grade-prose.sh` each unit `--signed` lists decoded (a `%20` in the `GRADED` field back to a space, a `%25` back to `%`), with the `REQUIREMENTS.md` beside the file named before `#`, so a heading unit whose heading holds a space, a `%` or a `/` is graded under its own name; a `GRADED` line present at the merge base, one a conflict resolution duplicated from the default branch among them, is not listed as one the branch signed. The listing's exit seeds the block's highest exit code.
   After the units the run signed, the block runs `$S/grade-prose.sh --convert` on the tree, so a unit the default branch signed under a formula the branch replaces is re-signed under the tree's before the rebased tip's full suite; its exit is folded into the block's highest exit code.
   Right after the block, with or without a rebase, commit the `GRADED` files the block modified, and only those (a `GRADED` file modified before the block stays out), as `docs: regrade the prose the branch signed (#<n>)`; when it modified none, commit nothing.

   Run `$S/refactor-owed.sh list .tdd/issue-<n>-refactor-owed.md` once, before the PR is readied.
   When it prints a candidate (exit 0), then and not before, run the issue's one structural pass:
   `Read` and run `<base directory>/STRUCTURAL.md`. On exit 3 the run never reads it.
   No candidate — `list` exits 3, and a missing `.tdd/issue-<n>-refactor-owed.md` is the
   `list` exit-3 case — skips the pass with no bail: it is marked `stopped=nothing-structural`
   before the PR is readied:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh structural-pass stopped=nothing-structural
   ```
   After `pr-prepare.sh`, run `$S/pr-checks.sh <n>`, and again on exit 3: it makes this sub-step's checks from the lint
   run to `unwired.sh` below in one call. On exit 0 take `candidates=` (the candidates issue's url, empty for none) from
   its last line and go on to sub-step 2; on exit 1 or 2 go on by the check its last line, `stopped at <check> <what>`,
   names, from that check's prose below.
   After the structural pass (or this skip) and before `refactor-candidates.sh`, each time the run
   enters this step, run the repo's declared lint command once, at the worktree root (the
   conductor's working directory), through `detach-command.sh`. The command is the one
   `$S/detect-test-command.sh --tier lint` prints from the repo CLAUDE.md's `veri: lint: <command>`
   line; veri never guesses one. The block first empties `.tdd/issue-<n>-lint.md`, so a section an
   earlier entry wrote never outlives this one:
   ```
   : > .tdd/issue-<n>-lint.md
   lint="$($S/detect-test-command.sh --tier lint)"; found=$?
   [ "$found" != 0 ] || $S/detach-command.sh start lint sh -c "$lint"
   ```
   `--tier lint` exit **3** (no `veri: lint:` line) runs nothing, writes no event and adds no PR
   body section: go on to `refactor-candidates.sh`. Its exit **2** (no answer could be obtained)
   runs nothing and writes no event either, and the section says so: write
   `### Lint` followed by `The lint command could not be read: detect-test-command.sh --tier lint
   exited 2.` to `.tdd/issue-<n>-lint.md`. On exit **0**, wait on the run in the foreground, the
   whole wait bounded by `VERI_LINT_TIMEOUT` (default 1800 seconds), counted from the lint's
   `start`, so calling `wait` again never extends it:
   ```
   $S/detach-command.sh wait lint --total "${VERI_LINT_TIMEOUT:-1800}" > /dev/null 2> .tdd/lint.wait.err; waited=$?; [ "$waited" != 3 ] || exit 0    # exit 3: still running → run this line and every line after it again, in a new Bash call
   [ "$waited" = 2 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh lint exit="$(cat .tdd/lint.exit)"
   ```
   `wait` exit **0** (the command exited 0) or **1** (it exited non-zero) writes
   `event.sh lint exit=<code>`, the code `.tdd/lint.exit` holds, and then the `### Lint` section:
   ```
   lint="$($S/detect-test-command.sh --tier lint)"; code="$(cat .tdd/lint.exit)"
   { printf '### Lint\n\n'
     if [ "$code" = 0 ]; then printf '`%s` passed.\n' "$lint"
     else printf '`%s` exited %s. The last 20 lines of its output:\n\n~~~text\n' "$lint" "$code"
       tail -n 20 .tdd/lint.out | cut -c1-300
       printf '~~~\n'; fi; } > .tdd/issue-<n>-lint.md
   ```
   Each of those lines is cut at 300 characters, so the section stays far inside GitHub's body
   limit and a long line cannot make `pr-body.sh` fail. The file holds the output as the command
   printed it; `pr-body.sh` redacts it on the way out (below). `wait` exit **2** means no exit code was recorded:
   first run `$S/stop-requested.sh`: on `now` the run goes to *Stopping* (`Read` and run
   `<base directory>/STOPPING.md`) and does not bail. Otherwise, when `.tdd/lint.wait.err` holds
   `still running past --total`, the bound expired: `wait` stopped the command with its process
   group, no event is written, and the section is `### Lint` followed by
   `` `<command>` did not finish within VERI_LINT_TIMEOUT (<seconds> seconds) and was stopped. ``
   Otherwise the command could not be run (it died
   before recording an exit), so no event is written and the section is `### Lint` followed by
   `` `<command>` could not be run: no exit code was recorded. `` — each reported as neither a pass nor a
   failure of the lint. A lint that could not be run or read, or was stopped at the bound, neither
   bails the run nor holds the PR: the section reports it and the step goes on. Sub-step 2 puts the
   file's contents, when it is non-empty, in the PR body. `pr-body.sh` redacts every line of the
   body it writes: each local path (the worktree, the main clone, a temp directory, the home
   directory), the host name and the account name, then the tokens and secrets `comment.sh`'s rule
   names, so nothing the lint printed about this machine reaches the PR.
   On a non-zero lint exit (`wait` exit 1), once the section is written, append one repair step
   after the last done step, carrying `⟦diff-checked⟧ ⟦lint-repair⟧`. `$S/lint-repair.sh step` composes its text: the command, read from
   the repo's CLAUDE.md, and its output's first non-empty line, capped at 200 characters and with
   every local path, the host and the account name redacted. Its exit **3** (no `veri: lint:` line
   declared) appends no step and writes no bail, and the section gains `No repair step could be
   added.`; its exit **2** (no answer could be obtained) appends no step and **bails** as a system
   failure with cause `no-verdict` (`Read` `<base directory>/BAIL.md`):
   ```
   text="$($S/lint-repair.sh step < .tdd/lint.out)"; made=$?
   [ "$made" != 3 ] || { printf '\nNo repair step could be added.\n' >> .tdd/issue-<n>-lint.md; exit 0; }
   [ "$made" != 2 ] || { VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=no-verdict classification="$($S/classify-bail.sh no-verdict)"; exit 0; }
   $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" "$text" 2> .tdd/add-ledger-step.err; rc=$?
   [ "$rc" != 2 ] || { $S/adjudicate.sh left <n> && { echo "adjudicate step-add-refused"; exit 0; }; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=step-add-refused classification="$($S/classify-bail.sh step-add-refused)"; }
   [ "$rc" != 0 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
   [ "$rc" != 0 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the lint findings (#<n>)"; }
   ```
   Exit **0** returns to step 3, *The cycle loop*: the step runs as any `⟦diff-checked⟧` step does
   (`Read` `<base directory>/DIFF-CHECKED.md`), and the run comes back to this step and runs the
   lint again. Exit **2** bails `step-add-refused`, adjudicated first exactly as the full-suite
   repair block's exit 2 is (`Read` `<base directory>/BAIL.md`). Exit **1** appends no step and
   writes no bail, since a lint finding is not a broken product and a bail at the last step would
   lose a finished run: it is the one repair per run already spent (`.tdd/add-ledger-step.err`
   names `already inserted a lint-repair step`), and the section gains the line `The command is
   not clean after one repair step.`, or the plan's growth budget spent, and the section gains
   `No repair step could be added.`; either way the step goes on.
   **The test-quality check.** After the lint run (or its skip) and before `refactor-candidates.sh`,
   unless `.tdd/issue-<n>-test-quality` exists (an earlier entry of this step recorded it, so a
   resume does not pay for the leaf again), list the test files the run's range touched: those
   `git diff --name-only <branch-base>..HEAD` names that `case_reader.is_test_path` accepts and
   that still exist, `<branch-base>` being `git merge-base HEAD origin/<default>`:
   ```
   $S/test-quality.sh files "$(git merge-base HEAD origin/<default>)" > .tdd/test-quality-files; files=$?
   ```
   Exit **3** (no test file touched) launches no leaf: write the record empty,
   `: > .tdd/issue-<n>-test-quality`, and go on. Exit **2** is a system failure: **bail** with
   cause `no-verdict` (`Read` `<base directory>/BAIL.md`). On exit **0**, record `HEAD`, then launch
   one `develop-test-quality` leaf **through the supervisor**, prompted with the spec, the test
   command and those files:
   ```
   git rev-parse HEAD > .tdd/test-quality-head
   $S/build-develop-prompt.sh test-quality .tdd/issue-<n>-spec.md '<test-cmd>' $(cat .tdd/test-quality-files) > .tdd/develop-test-quality.prompt
   rm -f .tdd/develop-test-quality.exit .tdd/develop-test-quality.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-test-quality $S/run-leaf.sh .tdd/develop-test-quality.prompt --permission-mode bypassPermissions > .tdd/develop-test-quality.out 2> .tdd/develop-test-quality.err
   $S/wait-leaf.sh develop-test-quality   # foreground; on exit 3 call it again
   ```
   A supervisor exit 2 on the leaf is a `killed-stuck` bail, as for any developer leaf. The leaf
   has no verifier, so it may change nothing: when it leaves a changed working tree or a commit
   (`git status --porcelain` prints anything, or `HEAD` is not the sha
   `.tdd/test-quality-head` holds), put the branch back first with
   `git reset --hard "$(cat .tdd/test-quality-head)" && git clean -fd`, and still record its
   report:
   ```
   $S/test-quality.sh record <n> < .tdd/develop-test-quality.out
   ```
   Exit **0** (findings recorded) and exit **3** (`FINDING: none`, the record written empty) go on.
   A finding naming no `<file>::<case>`, or a case its file does not define, is skipped and named on
   stderr; the others are still recorded. Exit **2** (nothing recorded: no `FINDING:` line, or every
   finding refused) is a system failure: **bail** with cause `no-verdict` (`Read` `<base directory>/BAIL.md`).
   **Test-quality fixes.** Then, each time the run enters this step and the record holds findings
   (`record` exited 0 on this entry, or an earlier entry's record is non-empty), the run fixes the
   `weak-assertion` and `implementation-coupled` ones itself, each in a step of its own. A
   `redundant` finding gets no step: which of two cases is redundant is the reviewer's call. Take
   the record's `weak-assertion` and `implementation-coupled` lines in recorded order, skip each whose
   `<file>::<case>` a `⟦test-quality⟧` step of the committed ledger already names (a resume, or an
   entry after those steps ran, appends none twice), and keep the first ones up to
   `${VERI_TEST_QUALITY_FIXES:-1}` less the `⟦test-quality⟧` steps the ledger already holds — that
   knob is a budget on an axis of its own (cost: the test-quality steps one run may add), never
   folded into another, and `0` appends none. For those findings, append all their steps in one
   call after the anchor `$S/test-quality.sh anchor` prints: the last done step carrying exactly one
   `⟦criterion k⟧` tag, which the appended steps inherit. Its exit **3** — no such step, or a ledger
   step carrying two tags, which `add-ledger-step.sh` would refuse — appends nothing and leaves those
   findings unfixed with no bail, as a growth refusal does; its exit **2** (the ledger unreadable)
   bails `no-verdict` (`Read` `<base directory>/BAIL.md`). Each text names the case, the kind and the why, saying it edits
   only that case and no production code, and ending `⟦test-quality⟧ ⟦diff-checked⟧` (in that order,
   so the inserted `⟦added⟧ ⟦criterion k⟧` follows `⟦diff-checked⟧`):
   ```
   step="$($S/test-quality.sh anchor .tdd/issue-<n>.md)" || exit 0    # exit 3 or 2: routed as above, no step appended
   $S/add-ledger-step.sh .tdd/issue-<n>.md after "$step" '<fix the <kind> case <file>::<case>: <why>; edit only that case, no production code> ⟦test-quality⟧ ⟦diff-checked⟧' … 2> .tdd/add-ledger-step.err; rc=$?
   [ "$rc" != 0 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=<count>
   ```
   The `step-added` event is written only on exit 0, after the insertion has happened. Exit **0**: `git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: fix the test-quality findings (#<n>)"`,
   and return to step 3, *The cycle loop*, without readying the PR. Exit **1** (`VERI_STEP_GROWTH_PERCENT`
   cannot hold them, the texts filed under `## Owed steps`) leaves those findings unfixed and writes
   no bail: a quality fix is never worth losing a finished run; commit the ledger as on exit 0 and go
   on. Exit **2** bails with cause `step-add-refused` (`Read` `<base directory>/BAIL.md`). Each
   appended step runs as any `⟦diff-checked⟧` step, its flip proving the fix
   (`<base directory>/DIFF-CHECKED.md`).
   After the structural pass (or its skip) and before `refactor-candidates.sh`, run
   `$S/red-setup.sh worst <n> .tdd/issue-<n>-refactor-owed.md` once. It reads the run's `red-setup`
   events (the latest per step) and, when the highest count exceeds `VERI_SETUP_THRESHOLD` (default 3),
   records that one step as a `testability` `not-done` row of the owed file, replacing the row an
   earlier entry recorded, so the candidates issue lists it. Exit **0** (recorded) and exit **3** (no
   step over the threshold) go on; exit **2** is a system failure: **bail** with cause `no-verdict`
   (`Read` `<base directory>/BAIL.md`).
   After the lint run (or its skip) and before `refactor-candidates.sh`, each time the run enters
   this step, run `$S/coupling.sh <branch-base>` once, `<branch-base>` being the merge base with
   `origin/<default>`. The block first empties `.tdd/issue-<n>-coupling.md`, so a section an
   earlier entry wrote never outlives this one:
   ```
   : > .tdd/issue-<n>-coupling.md
   $S/coupling.sh "$(git merge-base HEAD origin/<default>)" > .tdd/coupling.out; coupling=$?
   [ "$coupling" != 0 ] || { printf '### Coupling\n\n'; cat .tdd/coupling.out; } > .tdd/issue-<n>-coupling.md
   ```
   Exit **0** printed each pair of same-extension code files, at least one changed by the run,
   that name each other (`mutual: <a> <b>`): the block wrote them all, under `### Coupling`, to
   `.tdd/issue-<n>-coupling.md`, which sub-step 2 puts in the PR body. Then record exactly one
   row, for the printed pair whose two files the range changed the most lines in (`git diff
   --numstat <branch-base>..HEAD`, added plus deleted, summed over the two files), the first
   printed on a tie, since `coupling.sh` prints in byte order:
   ```
   $S/refactor-owed.sh not-done .tdd/issue-<n>-refactor-owed.md 'mutual reference: <a> <b>' coupling
   git add -f .tdd/issue-<n>-refactor-owed.md; git diff --cached --quiet || git commit -m "chore: record the run's coupling candidate (#<n>)"
   ```
   `not-done` keeps one `coupling` row per file, so a resume's call replaces the row an earlier
   entry recorded rather than adding one; `refactor-candidates.sh` lists it and the structural
   pass never takes it. Exit **3** (no pair) records nothing and drops a row an earlier entry
   recorded, then goes on:
   ```
   $S/refactor-owed.sh clear .tdd/issue-<n>-refactor-owed.md coupling
   git add -f .tdd/issue-<n>-refactor-owed.md; git diff --cached --quiet || git commit -m "chore: drop the run's stale coupling candidate (#<n>)"
   ```
   When `pr-checks.sh` stopped at coupling with `red-setup.sh worst <n> .tdd/issue-<n>-refactor-owed.md changed the
   owed file`, coupling found no pair but the `red-setup.sh worst` row is not committed yet: commit it, then run
   `pr-checks.sh` again:
   ```
   git add -f .tdd/issue-<n>-refactor-owed.md; git diff --cached --quiet || git commit -m "chore: drop the run's stale coupling candidate (#<n>)"
   ```
   Exit **2** (the base did
   not resolve) is a system failure: **bail** with cause `no-verdict` (`Read`
   `<base directory>/BAIL.md`). Only mutual references are reported; upward imports are not.
   After the coupling run and before the PR is readied, run
   `$S/refactor-candidates.sh <n> .tdd/issue-<n>-refactor-owed.md` once. Exit **0** prints the
   candidates issue's url, which goes in the PR body's `## Refactor owed` section; exit **3**
   (nothing out-of-bounds or not done) does nothing; exit **2** is a system failure: **bail**
   with cause `no-verdict` (`Read` `<base directory>/BAIL.md`). The candidates issue is never
   labelled with the opt-in label (`VERI_LABEL`) and is filed at most once per run: a resume
   runs the same command and it replaces the existing issue's body.
   After `refactor-candidates.sh` and before the PR is readied, each time the run enters this
   step, run `$S/unwired.sh --accepted .tdd/issue-<n>-unwired-accepted <branch-base>` once,
   `<branch-base>` being the merge base with `origin/<default>`:
   ```
   $S/unwired.sh --accepted .tdd/issue-<n>-unwired-accepted "$(git merge-base HEAD origin/<default>)" > .tdd/unwired.out; unwired=$?
   [ "$unwired" != 1 ] || cat .tdd/unwired.out >> .tdd/issue-<n>-unwired-pending
   [ "$unwired" != 1 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=unwired classification="$($S/classify-bail.sh unwired)" failed="$(cat .tdd/unwired.out)"
   ```
   It checks only code: an added prose, config or data file and a path under `.github/` are
   never printed. Exit **1** printed each added code file whose stem no other non-test file
   names and that the accepted record does not list: the second line adds those files to
   `.tdd/issue-<n>-unwired-pending`, never to the accepted record, and the third **bails** with
   cause `unwired`, naming every file it printed, and the PR is left a draft (`Read`
   `<base directory>/BAIL.md`). Only the human's `release-issue.sh <n>` after that bail turns the
   pending record into accepted files, so a resume without a release bails `unwired` again, and
   a released run's resume goes on when every file it would print is accepted and bails `unwired`
   again when one is not. Exits **0** (every such file is named or accepted) and **3** (the range
   adds none) go on. Exit **2** (the base did not resolve, or no work tree) is a system
   failure: **bail** with cause `no-verdict` (`Read` `<base directory>/BAIL.md`).
2. **Mark the PR ready for review only once the run's metrics are cut with the PR's URL, rendered, committed and
   pushed; then read its CI, close the run's log with the PR's URL, and rewrite the PR into its final form** — one
   sub-step, in this order, from inside the worktree. Every commit the run's record owes (the `⟦full-suite⟧` ticks owed to
   CI, the `metrics:` commit) is pushed before `pr-ready.sh`, so no records-only push follows the readied PR: the
   `ready_for_review` run is the one `gates` run, unless a code change (a `⟦ci-repair⟧` step, a rebase) starts another.
   The `done` mark, which every reader of a run's end (`run-finished.sh`, the run's activity, the conductor's needs-user
   check) takes as the run finished, is still written only once CI's first wait is green, and it is never committed or
   pushed. **This step opens no PR.** Step 2.3 opened it at the plan commit, so
   there is nothing left here for a PR-creating `gh api` call to do: a second one against a branch that
   already has an open PR is either a refusal that ends the run at its last step, or a second
   PR for the same branch — and then the claim another machine reads and the page a human is
   asked to merge are two different pages. Before the first block, run `$S/pr-ready-wait.sh <n>`, and again on exit 3; on
   exit 0 take `pr_url`, `pr_number`, `ci=`, `metrics=` (there only when the render failed, holding `metrics.sh`'s exit)
   and `no_checks=` from its last lines (the record is committed and pushed, the PR readied and its first `wait-ci.sh`
   exited 0: go on after the first block); on any other exit go on by the first block from the point its last line
   names, the `pr-ready-failed` bail included. A stacked run never calls it (it refuses one with exit 2,
   `.tdd/issue-<n>-base` present), and a missing ledger or a `git` or `gh` call that fails inside it is its exit 2. Read the existing PR's URL rather than assuming the
   run remembers it, so a resumed run edits the PR its branch already has:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   # Only under VERI_BRANCH_SUITE=ci (the mode $S/branch-suite.sh printed) with a ⟦full-suite⟧ line still unchecked: tick each such line with $S/tick-ledger.sh and its issue criterion with
   # $S/tick-issue-criterion.sh as the ⟦full-suite⟧ paragraph above describes, owed to CI (no CI wait has spoken yet, and none is read), then
   #   git add .tdd/issue-<n>.md && git commit -m "plan: the full suite is owed to CI (#<n>)"
   # In every other case skip this: the lines were ticked after a green local run, or none is left.
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh metrics-cut pr=<pr-url>
   $S/metrics.sh <n> > .tdd/issue-<n>-metrics.md; metrics=$?
   if [ "$metrics" = 0 ]; then
     git add .tdd/issue-<n>-metrics.md
     git commit -m "metrics: what solving #<n> cost (#<n>)"
   fi
   $S/push-branch.sh
   blocked=; $S/pr-ready.sh <pr-number> "$(git rev-parse HEAD)" 2> .tdd/pr-ready.err || blocked=1
   # On `pr-ready.sh` exit 2 the next line writes the bail only when `adjudicate.sh left` exits non-zero (3, no budget left; 2, the event log unreadable); with budget left it writes nothing and ends the call (`exit 0`, printing `adjudicate pr-ready-failed`), and the exit is adjudicated before any event and any `wait-ci.sh` call, as the `pr-ready.sh` paragraph after this block says (`Read` `<base directory>/ADJUDICATE.md`).
   [ -z "$blocked" ] || { $S/adjudicate.sh left <n> && { echo "adjudicate pr-ready-failed"; exit 0; }; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=pr-ready-failed classification="$($S/classify-bail.sh pr-ready-failed)"; }
   [ -n "$blocked" ] || $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" > .tdd/wait-ci.out 2> .tdd/wait-ci.err; ci=$?; [ "$ci" != 3 ] || exit 0    # exit 3 ends the call → run this line and every line after it again, in a new Bash call
   # The flake check, the CI flake paragraph after this block: on exit 1 the next line empties .tdd/ci-flake.out, reads the head's failed CI runs, and with exactly one saves its failed log and runs ci-flake.sh; its exit 0 ends the call (`exit 0`, printing `ci-flake re-run`) → run the wait-ci.sh line above and every line after it again, in a new Bash call; its exit 1, 2 or 3, a `gh` failure, a head with no failed run or with more than one, or no `veri: one test file:` line (detect-test-command.sh exit 3) goes on to the lines below, the red unchanged.
   [ "$ci" != 1 ] || { : > .tdd/ci-flake.out; perl -e 'alarm shift; exec @ARGV' "${VERI_GH_TIMEOUT:-300}" gh run list --commit "$(git rev-parse HEAD)" --status failure --json databaseId -q '.[].databaseId' > .tdd/ci-flake-run && [ "$(grep -c . .tdd/ci-flake-run)" = 1 ] && perl -e 'alarm shift; exec @ARGV' "${VERI_GH_TIMEOUT:-300}" gh run view "$(cat .tdd/ci-flake-run)" --log-failed > .tdd/ci-failed.log && alone="$($S/detect-test-command.sh --tier "one test file")" && $S/ci-flake.sh <n> "$(git rev-parse HEAD)" "$(cat .tdd/ci-flake-run)" "$alone" .tdd/ci-failed.log > .tdd/ci-flake.out && { echo "ci-flake re-run"; exit 0; }; }
   [ "$ci" != 0 ] || [ ! -s .tdd/ci-flake.out ] || { VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh ci-flake head="$(git rev-parse HEAD)" run="$(cat .tdd/ci-flake-run)" files="$(paste -sd , .tdd/ci-flake.out)" && cat .tdd/ci-flake.out >> .tdd/ci-flakes.txt && : > .tdd/ci-flake.out; }    # a green wait after a re-run: the flake, its run the one ci-flake.sh re-ran
   grep -F 'conflicts with its base branch' .tdd/wait-ci.err > /dev/null; conflict=$?
   # A `wait-ci.sh` exit 2 naming no conflict is adjudicated first, before the `ci-timeout` bail event (`Read` `<base directory>/ADJUDICATE.md`): the next line writes that bail only when `adjudicate.sh left` exits non-zero (3, no budget left; 2, the event log unreadable). With budget left it writes nothing and ends the call (`exit 0`, printing `adjudicate ci-timeout`), so no later line of it runs; run the adjudication, then a `retry` runs `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"` and, in one new Bash call, the `wait-ci.sh` line above and every line after it, its exits handled as at the first wait; any other outcome runs, alone in a Bash call of its own, `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"`, and no later line of this block runs.
   [ "$ci" != 2 ] || [ "$conflict" = 0 ] || { $S/adjudicate.sh left <n> && { echo "adjudicate ci-timeout"; exit 0; }; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"; }
   graded=1; [ "$ci" != 2 ] || [ "$conflict" != 0 ] || { $S/rebase-onto-default.sh --graded-only > .tdd/graded-rebase.out; graded=$?; }
   # A second conflict is adjudicated first, before the `ci-conflict` bail event: the next line writes that bail only when `adjudicate.sh left` exits non-zero (3, no budget left; 2, the event log unreadable). With budget left it writes nothing and ends the call (`exit 0`, printing `adjudicate ci-conflict`), so no later line of it runs; run the adjudication the conflict paragraph after this block gives, with `.tdd/wait-ci.err` as the stderr file (`Read` `<base directory>/ADJUDICATE.md`); that paragraph names the command each outcome runs.
   [ "$ci" != 2 ] || [ "$conflict" != 0 ] || [ "$graded" = 0 ] || [ ! -e .tdd/ci-conflict-rebased ] || { $S/adjudicate.sh left <n> && { echo "adjudicate ci-conflict"; exit 0; }; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"; }
   [ "$ci" != 1 ] || gh run view <run-id> --log-failed          # a failed check only → its suite and FAIL - line
   [ "$ci" != 1 ] || ! $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(cat .tdd/wait-ci.out)"
   [ "$ci" = 0 ] || [ "$ci" = 2 ] || $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null; no_repair=$?
   [ "$no_repair" = 0 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
   [ "$no_repair" = 0 ] || $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the CI failure: <suite> — <its FAIL - line>> ⟦ci-repair⟧' 2> .tdd/add-ledger-step.err
   [ "$no_repair" = 0 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red CI check (#<n>)"; }
   ```
   That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
   **`add-ledger-step.sh` exit 2** on the `⟦ci-repair⟧` insertion, its stderr kept in `.tdd/add-ledger-step.err`: with `$S/adjudicate.sh left <n>` exit 0, first launch `adjudicate-step-add-refused` through `supervise.sh`, before any `bail` event (`Read` `<base directory>/ADJUDICATE.md`); then, whatever the answer (`retry` included), or on `adjudicate.sh left` exit 3 or 2, **bail** with cause `step-add-refused` by running, alone in a Bash call of its own, `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=step-add-refused classification="$($S/classify-bail.sh step-add-refused)"`, calling `add-ledger-step.sh` no more — see `<base directory>/BAIL.md`.
   When `pr-ready.sh` exits non-zero (it exits only 0 or 2), its stderr is kept in `.tdd/pr-ready.err` and the exit is adjudicated
   first, before any event and any `wait-ci.sh` call, in the order `ADJUDICATE.md`'s *Procedure* gives (`Read` `<base directory>/ADJUDICATE.md`):
   the block's `$S/adjudicate.sh left <n>` runs first, and its exit 3 (a spent budget, `VERI_ADJUDICATE_BUDGET=0` included) or 2 (the event log unreadable) writes the bail on that same line.
   On its exit 0 that line writes nothing and ends the Bash call (`exit 0`, printing `adjudicate pr-ready-failed`); then, in Bash calls of their own, run
   `$S/build-adjudicate-prompt.sh <n> pr-ready-failed 2 .tdd/pr-ready.err pr-ready.sh <pr-number> "$(git rev-parse HEAD)" > .tdd/adjudicate-pr-ready-failed.prompt`,
   the `adjudicate-pr-ready-failed` leaf launched through `supervise.sh` and waited on, then
   `$S/adjudicate.sh record <n> pr-ready-failed .tdd/adjudicate-pr-ready-failed.out`, which writes the `adjudicated` event.
   `retry` (exit 0) runs `$S/pr-ready.sh <pr-number> "$(git rev-parse HEAD)" 2> .tdd/pr-ready.err` once more: in one new Bash call, run the block again from
   `blocked=; $S/pr-ready.sh <pr-number> "$(git rev-parse HEAD)" 2> .tdd/pr-ready.err || blocked=1` through its last line, so its exit 0 goes on to the
   `wait-ci.sh` line as a first-call exit 0 does, and its exit 2 is handled as at the first call.
   `bail`, any `route` (`pr-ready-failed` lists none) or an unparsed answer (`adjudicate.sh record` exit 2, the leaf's own no-answer included)
   runs, alone in a Bash call of its own,
   `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=pr-ready-failed classification="$($S/classify-bail.sh pr-ready-failed)"`,
   and no later line of the block runs. So when no adjudicated `retry` of it exits 0, the block writes its
   `adjudicated` events, then the `pr-ready-failed` bail, and nothing else: no `wait-ci.sh` call follows (in the first call `blocked` makes the wait line skip it and leave `ci` at 0), so no CI deadline is started, no `ci-timeout`, `ci-conflict` or `ci-red` bail follows, no `step-added` event, `⟦ci-repair⟧` ledger line or `plan: repair the red CI check` commit is made and no `gh run view` is asked for. The run **bails** as a **system** failure (`pr-ready-failed`, classified by `classify-bail.sh`) with the PR left a draft, the bail comment carrying the text of `.tdd/pr-ready.err` as its last reason (`Read` `<base directory>/BAIL.md`).
   A `pr-ready-failed`, `ci-timeout`, `ci-conflict` or `ci-red` bail ends the step there, and neither the `done` mark nor
   the second block nor sub-step 4's done comment follows it: the `metrics-cut` mark and the `metrics:` commit came
   before readying, and the bail is written after them, as the log's last ending (`Read` `<base directory>/BAIL.md`). Once the first `wait-ci.sh` exited 0, before
   the second block, run `$S/pr-finish.sh <n>`; it makes no wait, so it never exits 3. On exit 0 take
   `.tdd/issue-<n>-refactor-owed-render`, the body's render, from its last lines, and go on at the block's title
   `gh api -X PATCH` line; on any other exit go on by the second block from the point its last line names. It only reads
   the PR's url, writes the `done` mark and renders: it makes no commit, no push and no CI wait, so the PR stays on the
   head CI just read. The
   PR's title and body stay the conductor's. A stacked run never calls it either (exit 2 with `.tdd/issue-<n>-base`
   present); a failing `git` or `gh` call is its exit 2. Otherwise:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>    # CI's first wait is green: only now is the run read as done
   $S/refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md
   gh api -X PATCH repos/{owner}/{repo}/pulls/<pr-number> -f title="<type>: <criterion summary> (#<n>)"
   $S/ledger-growth.sh split .tdd/issue-<n>.md > .tdd/issue-<n>-growth.md; growth=$?
   cat > .tdd/issue-<n>-pr-body.md <<'EOF'
   <Closes #<n> — summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed; followed by the contents of .tdd/issue-<n>-metrics.md (or, when $metrics is not 0, the line 'metrics could not be rendered: metrics.sh exited $metrics' in its place), followed by that render's output, followed by, when $growth is 0, a ## Plan growth section holding .tdd/issue-<n>-growth.md and saying the owner is strongly advised to split the work after the criterion it names (when $growth is 2, the section holds the one line 'plan growth could not be measured: ledger-growth.sh split exited 2'; when 3, there is no such section), followed by the ledger's ## Owed steps bullets, followed by the conductor's mutation-parity.sh report as the pairs table, followed by its ⟦human-owed⟧ lines and each row that report owes under ## Owed by a human; when .tdd/ci-flakes.txt is non-empty, the line 'CI flakes, green on a re-run: <its targets, comma-joined>'; and, when .tdd/issue-<n>-skip-verify is non-empty, the line '⚠️ Unverified phases: <list>'; and, when $S/pr-ready-wait.sh printed no_checks=1, the line '⚠️ CI ran no checks on the readied head: the ⟦full-suite⟧ ticks were owed to CI and nothing proved them.'; and, when .tdd/issue-<n>-lint.md is non-empty, its contents, the ### Lint section; and, when .tdd/issue-<n>-coupling.md is non-empty, its contents, the ### Coupling section; and the ### Test quality section: one bullet per line of .tdd/issue-<n>-test-quality giving its kind, its <file>::<case> and its why, marked 'fixed' with the subject of the test: commit its ⟦test-quality⟧ step made, or 'not fixed' with why: 'redundant', 'budget' (past VERI_TEST_QUALITY_FIXES), 'step growth' (its step filed under ## Owed steps) or 'no anchor' (test-quality.sh anchor exited 3), or, when the file is empty, the line 'No weak-assertion, redundant or implementation-coupled case was found.'>
   EOF
   $S/pr-body.sh <pr-number> .tdd/issue-<n>-pr-body.md
   ```
   **`add-ledger-step.sh` exit 2** on the `⟦ci-repair⟧` insertion, its stderr kept in `.tdd/add-ledger-step.err`: with `$S/adjudicate.sh left <n>` exit 0, first launch `adjudicate-step-add-refused` through `supervise.sh`, before any `bail` event (`Read` `<base directory>/ADJUDICATE.md`); then, whatever the answer (`retry` included), or on `adjudicate.sh left` exit 3 or 2, **bail** with cause `step-add-refused` by running, alone in a Bash call of its own, `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=step-add-refused classification="$($S/classify-bail.sh step-add-refused)"`, calling `add-ledger-step.sh` no more — see `<base directory>/BAIL.md`.
   No exit of `ledger-growth.sh split` bails the run, holds the PR back or asks for anything: a plan that grew past
   the bound went ahead, and `## Plan growth` only reports it.
   The title is set by `gh api -X PATCH`, the body by `$S/pr-body.sh <pr-number> <body-file>`, never a whole-body `-f body=…` replacement: `pr-body.sh` keeps every section the run did not author, so a `## Review notes` section appended after the body survives a resumed run's next write.
   The readied PR's CI is read fail-closed, the way the `merge` skill reads it: an empty
   rollup is a pass only where `wait-ci.sh` exits 0 on it because `VERI_CI_ON_PR=0`, or with `VERI_CI_ON_PR` unset the target `CLAUDE.md`'s
   `veri: ci on pr: 0` line, says no check will come or, with neither the variable nor the line set, no workflow
   triggers on `pull_request` (the PR body then carries the no-checks warning line), and otherwise never a pass; a completed check whose conclusion is anything other than
   `SUCCESS`, `NEUTRAL` or `SKIPPED` counts as failed. A pending check never counts as
   green, and the wait is `wait-ci.sh`, one bounded slice per Bash call, given the full 40-hex sha just
   pushed (`git rev-parse HEAD`; an abbreviated one exits 2) so a rollup still reporting the previous head reads as pending: its exit 3 means a
   check is still pending, so call it again in a new Bash call; its exit 2 — a check still
   pending past the deadline its first call recorded, checks still queued `VERI_CI_QUEUE_WAIT` seconds after the first call that saw them queued, a ready, mergeable PR whose head has no check run and no commit status for `VERI_CI_NO_RUN_WAIT` seconds (default 600, a non-negative whole number; the grace restarts for each new head) while a `pull_request` workflow exists, its stderr naming `no CI run for <sha>` with the full 40-hex head, a PR still reporting a head other than the sha just pushed `VERI_CI_HEAD_WAIT` seconds after the first call that saw it, its one stderr line naming both shas, or `gh` unable to read the checks until that deadline (a 4xx other than 403 or 429 at once, a rate limit whose reset falls at or past that deadline at once; a rate limit on any read whose reset falls past the call's slice end waits only to the slice end and ends the call with exit 3) — does
   **bail**, with cause `ci-timeout`, rather than waiting on (`Read` `<base directory>/BAIL.md`).
   A `wait-ci.sh` exit 2 naming no conflict is adjudicated first, before the `ci-timeout` bail event (`Read` `<base directory>/ADJUDICATE.md`): a `retry` runs `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"` and then the same `wait-ci.sh` line once more, its exits handled as at the first wait; any other outcome runs `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"` alone in a Bash call of its own, and a spent budget or an unreadable event log writes that bail on the block's `adjudicate.sh left` line, whose exit 0 ends the call, as the comment in each block says.
   That deadline is `wait-ci.sh`'s own bound, since the call gives no total-seconds: twice the
   mean of the last 5 completed CI runs, capped at 10 minutes, or 540 s when fewer than 5
   exist or `gh` cannot answer.
   A failed check does not bail: read its run's log with `gh run view <run-id> --log-failed`,
   append a repair step to the ledger whose text quotes the failing suite and its `FAIL -`
   line — or the error line, when the suite died before writing one — commit the ledger, and
   return to step 3, *The cycle loop*, without the `done` mark: the quoted line is that step's red evidence, the same way
   a red full run's repair step is, and the step's `step-added` event follows the `metrics-cut` mark written before
   readying, so the next pass's report is cut afresh.
   A second red CI result after a CI repair step does **bail**, with cause `ci-red`, the way
   a second red full run does — the repair step is one more cycle, not a loop (`Read` `<base directory>/BAIL.md`).
   **CI flakes.** At every `wait-ci.sh` exit 1 — after `pr-ready.sh`, after a CI-conflict rebase or an
   adjudicated `retry`, each of which runs the block's `wait-ci.sh` line and the lines after it — before the
   red takes its `⟦ci-repair⟧` step or its `ci-red` bail, the block's flake line first empties `.tdd/ci-flake.out`, so a
   file left by an earlier attempt never labels a later green a flake. It takes `<run-id>` from
   `gh run list --commit <head-sha> --status failure --json databaseId -q '.[].databaseId'` into `.tdd/ci-flake-run`
   (this call and the `gh run view` below each bounded by `perl -e 'alarm shift; exec @ARGV' "${VERI_GH_TIMEOUT:-300}"`,
   so a `gh` with no answer ends as a `gh` failure):
   only a head with exactly one failed CI run is checked, since a head is re-run at most once; with none, or with
   several (a re-run of one would leave the others red), it checks nothing and the red takes its path unchanged. It then
   saves `gh run view <run-id> --log-failed` to `.tdd/ci-failed.log`, reads `<alone-cmd>` with
   `$S/detect-test-command.sh --tier "one test file"` and, unless that exits 3, runs
   `$S/ci-flake.sh <n> <head-sha> <run-id> '<alone-cmd>' .tdd/ci-failed.log`. Its exit 0 (every target
   passed alone and the failed jobs were re-run) runs the same `wait-ci.sh` line again; its exit 1, 2 or 3, a `gh`
   failure, or no `one test file` line, takes the path a red CI takes without it, unchanged. A `wait-ci.sh` exit 0 after
   that re-run is a flake: the block's next line writes `$S/event.sh ci-flake head=<sha> run=<run-id> files=<targets>`,
   `<run-id>` read back from `.tdd/ci-flake-run`, and keeps the
   targets in `.tdd/ci-flakes.txt` for the PR body; no `⟦ci-repair⟧` step is appended, and the run goes on as after any
   green wait. That wait's exit 1 is a real red:
   the flake line's `ci-flake.sh` exits 3 (the head was re-run) and the red takes the `⟦ci-repair⟧` step or the
   `ci-red` bail above; its exit 2 and 3 are handled as at any wait. A re-run is counted only by
   `VERI_CI_FLAKE_RERUNS`, never by `REVISE_BUDGET`, `VERI_ADJUDICATE_BUDGET` or the `⟦ci-repair⟧` count, and neither
   a re-run nor a `⟦ci-repair⟧` step returns the readied PR to draft.
   A conductor re-runs a failed CI job only through `$S/ci-flake.sh`: at most once per head and `VERI_CI_FLAKE_RERUNS`
   times per run (default 1; `0` re-runs none), and only after every test target the failed log names has passed
   alone. It never runs `gh run rerun` otherwise, and a re-run that is red again is a real red.
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
   the conflict is adjudicated first and **bails** with cause `ci-conflict` unless the adjudicator
   answers `retry` or `route rebase` (`Read` `<base directory>/BAIL.md`).
   That adjudication, at the `ci-conflict` site (the CI wait after `pr-ready.sh`, the block's one wait), runs before any
   `bail` event, in the order `ADJUDICATE.md`'s *Procedure* gives (`Read` `<base directory>/ADJUDICATE.md`): the block's `$S/adjudicate.sh left <n>`
   runs first, and its exit 3 or 2 writes the bail on that same line; on its exit 0 that line writes nothing and ends the Bash call (`exit 0`, printing `adjudicate ci-conflict`), so no later line of the block runs; then, in Bash calls of their own, run `$S/build-adjudicate-prompt.sh <n> ci-conflict 2 .tdd/wait-ci.err wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" > .tdd/adjudicate-ci-conflict.prompt`,
   the `adjudicate-ci-conflict` leaf launched through `supervise.sh` and waited on, then
   `$S/adjudicate.sh record <n> ci-conflict .tdd/adjudicate-ci-conflict.out`, which writes the `adjudicated` event. Then:
   - `retry` (exit 0): `$S/wait-ci.sh --fresh-window "$(git rev-parse HEAD)"`, then, in one new Bash call, the same `wait-ci.sh` line
     and every line of the block after it, its exits handled as at that wait; a conflict again returns to this adjudication.
   - `route rebase` (exit 1, printing `route rebase`): the one-rebase path again, `.tdd/ci-conflict-rebased`
     left in place — `$S/rebase-onto-default.sh` (no flag), its `develop-rebase` leaf and `verify-rebase` when it
     conflicts, the regrade block, under `VERI_REBASED_TIP_SUITE=local` the full suite once on the rebased tip, the push
     under the lease pinned to `<pre-rebase-sha>` — then, in one new Bash call, the same `wait-ci.sh` line and every line
     of the block after it; a conflict again returns to this adjudication, so the budget, not the marker, bounds the repeats.
     A `verify-rebase` REJECT there spends `REVISE_BUDGET`: it goes round the revise loop with phase `rebase`, and a spent
     budget bails `rebase-unresolved`, as on sub-step 1's path (`Read` `<base directory>/REVISE.md`).
   - `bail` (exit 1, printing `bail`) or an unparsed answer (`adjudicate.sh record` exit 2, the leaf's own no-answer included):
     alone in a Bash call of its own, `VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"`,
     its class `system`, and no later line of the block runs. A spent budget or an unreadable event log (`adjudicate.sh left` exit 3 or 2) wrote that bail on the block's line.
   A conflict with `.tdd/ci-conflict-rebased` absent, the run's first, is never adjudicated: it takes the one-rebase
   path above, as does a `--graded-only` exit 0.
   There too `rebase-onto-default.sh`'s exit code decides the next action, so nothing after it — the
   rebased tip's full test run in particular — is started until it has returned, and never in the
   same message as the rebase. Sub-step 1's own rebase takes no flag and does not change.
   No push follows the readied PR's CI read on the clean path: the `⟦full-suite⟧` ticks owed to CI and the `metrics:` commit
   were pushed before `pr-ready.sh`, and `pr-finish.sh`, the title PATCH and the body write commit nothing, so the
   `ready_for_review` run is the one `gates` run and no second `wait-ci.sh` is made. Only a code change starts another
   run: a `⟦ci-repair⟧` step's cycle, whose next pass through this step pushes its commits before `pr-ready.sh` and waits
   on the new head with the same block, or a rebase: the conflict rebase above, whose new head the same `wait-ci.sh`
   line reads, or the `merge` skill's before it merges, which reads CI on the head it merges.
   The `metrics-cut` mark comes before the render because `metrics.sh` reads it, in place of the `done` mark that
   only CI's green verdict writes, for both the Outcome and the issue's wall time: a report rendered before either
   exists says the run is still going and gives no wall time. No other reader takes the cut as the run's end, so
   `run-finished.sh`, the run's activity and the conductor's needs-user check read a run whose first CI wait is pending,
   or whose conductor died in it, as not done. The
   body is rewritten only after the `metrics:` commit is pushed, so it never quotes a file the
   branch does not yet carry. Since that commit is made before readying, the report counts neither the CI wait after
   readying nor `pr-finish.sh`: its `#### Total` says so in a line of its own, which the body, quoting the report whole,
   carries. The title drops the `WIP:` prefix step 2.3 opened it with, and
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
   `add-ledger-step.sh` could not fit inside `VERI_STEP_GROWTH_PERCENT`, which nothing in the run
   reads again — goes into the PR body under a `## Owed steps` heading of its own. A ledger
   carrying no such heading adds no such section.
   What a human still owes is copied last: every `⟦human-owed⟧` ledger line — a record of a
   manual check, which no cycle ticks — goes into the PR body under an `## Owed by a human`
   heading, each listed with its criterion number from its `⟦criterion k⟧` mark, so the
   reviewer sees which issue criterion is still waiting on them. A ledger holding no
   `⟦human-owed⟧` line adds no such section.
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Run `$S/run-done.sh <n>` first; it never exits 3. On exit 0 take `stop_requested=` (the first ask's exit) and
   `cleared=` from its last lines: the done comment is posted and a reported stop request cleared. On any other exit
   go on by this sub-step from the point its last line names. Its tree check before the comment leaves out
   `.tdd/issue-<n>-metrics.md` when `.tdd/issue-<n>-pr-ready-wait` holds a non-zero `metrics=`: a failed render's leftover.
   Before posting it, run `$S/stop-requested.sh`. Then post the final done comment by running
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

