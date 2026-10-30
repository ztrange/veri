## Revising on a REJECT

A `REJECT` (verify.sh exit **1**) does **not** stop the run. The conductor gets a bounded
**attempt budget** — `REVISE_BUDGET` revise attempts, **default 2** — to satisfy the blind
verifier before bailing the step. The rejection **reason is the carry-forward signal**:
leaves never share context, so each revise leaf is told explicitly what to fix.

A revise of red, green or refactor is built from a prompt that asks for no `SUITE:` line, so its wait
exits 0 straight into its verifier and nothing checks for the line. The `diff` revise does ask for one:
its check is stated under *A `⟦diff-checked⟧` step*.

The phases sent to `build-develop-prompt.sh revise <phase>` are red, green, refactor, transform, diff, rebase and the interface phases expand, migrate, contract-a, contract-b; a rejected transform is revised as `revise transform`, never mapped to `refactor`; a rebase rejection (the Draft PR step's rebase verifier) is revised as `revise rebase`.

A revise of green whose leaf reports `WRONG_TEST: <why>` is exempt from the `SUITE:` line and is routed as a
develop-green `WRONG_TEST:` report is, as is one carrying a `SUPERSEDED:` line, with or without `WRONG_TEST:`: `$S/wrong-test-route.sh .tdd/revise-green-<k>.out '<target-test-id>'` runs
before the attempt is counted; its exit 0 writes no `revise` mark, spends no `REVISE_BUDGET` attempt and launches
the `red-contradicted` red, its exit 3 keeps the attempt's main outcome, a verify-green REJECT, and its exit 2 is
a bail; never a `report-missing` bail.
A `repair <case>` answer launches `red-repair` over the revise-green report instead.
A revise of green answering `IMPOSSIBLE` with a `MISSING_TEST:` line is routed the same way (`$S/wrong-test-route.sh .tdd/revise-green-<k>.out '<target-test-id>'`), as is a verify-green or mutation-parity REJECT reason before any revise: on `missing <behaviour>` the conductor writes a `reroute` event, writes no `revise` mark, spends no `REVISE_BUDGET` attempt, launches the `red-missing` red with that file as its brief (`build-develop-prompt.sh red-missing`), sends the added case through verify-red (verify-pin when it reports `AGAINST_UNMODIFIED: PASSES`), re-records the step's frozen tests with `tests-frozen.sh record --step`, then runs green again.
The route runs with `VERI_STEP` set to the current step and its exit 0 writes a `reroute` event with `VERI_STEP` before the launch, carrying `kind=<kind>`. A `missing` route is free up to `VERI_MISSING_REROUTE_BUDGET` per step, and its exhaustion (`missing-exhausted`, exit 1) bails with cause `missing-reroutes-exhausted`; a repeat red, repair, supersede or fixture reroute in the step takes the revise path and spends one `REVISE_BUDGET` attempt.

For attempt `k = 1 … REVISE_BUDGET`:

1. **Same reason?** First, before anything about attempt `k` is posted or logged, save the reason
   attempt `k` answers under the attempt's own number, since the re-verify below (and, before it, the
   red prediction check and the green frozen-tests check) overwrites `.tdd/verify-<phase>.reason`:
   ```
   cp .tdd/verify-<phase>.reason .tdd/verify-<phase>-<k>.reason
   ```
   On attempt 1 there is no previous attempt, so the comparison is skipped. For each attempt after
   the first, run
   `$S/same-reject.sh .tdd/verify-<phase>-<k-1>.reason .tdd/verify-<phase>.reason; echo $?`: on exit 0
   (attempt `k-1` was rejected for the same reason it was revising) go to the `develop-exhausted` leaf
   without posting attempt `k`'s comment, writing its `revise` mark or launching it; on exit 1 or
   exit 2 continue the revise loop as today.
2. **Mirror.** Post a `### ♻️ Revise <phase> — attempt <k>/<REVISE_BUDGET>` comment carrying
   the verifier's **rejection reason verbatim**, and mark the same attempt in the log:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" VERI_PHASE=<phase> VERI_ATTEMPT=<k> $S/event.sh revise budget=<REVISE_BUDGET>
   ```
3. **Fresh developer leaf.** Build the revise prompt from the `revise` template, naming the
   phase being redone and the **reason file** the verifier's stdout went to, then launch
   **through the supervisor** (exit **2 → bail**, system failure, after the stop check in
   *Launching a leaf*). When `<phase>` is red, first run `$S/restore-production.sh <test-path>` (the
   step's test path from the Red report), so the relaunched red leaf inherits a tree with no
   production change beyond `HEAD` — a rejected green's uncommitted production edit is gone — while
   the red's own new or changed test is kept; its exit 2 is a bail, a system failure (`no-verdict`):
   ```
   $S/build-develop-prompt.sh revise <phase> .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' .tdd/verify-<phase>.reason '<fast-cmd>' > .tdd/revise-<phase>-<k>.prompt
   rm -f .tdd/revise-<phase>-<k>.exit .tdd/revise-<phase>-<k>.pid .tdd/red-prediction.md .tdd/red-run-output.txt
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh revise-<phase>-<k> $S/run-leaf.sh .tdd/revise-<phase>-<k>.prompt --permission-mode bypassPermissions > .tdd/revise-<phase>-<k>.out 2> .tdd/revise-<phase>-<k>.err
   $S/wait-leaf.sh revise-<phase>-<k>   # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — red or green only — see *The step's cost check*
   ```
   The `step-cost.sh` line runs only when `<phase>` is red or green: a refactor-phase revise
   never runs it, because the refactor phase comes after the step's green commit and *The
   step's cost check* runs no check past that commit.
   The reason travels as a **file**, not as prose you paste in — that is why the verify step
   redirected it. The template tells the leaf it is fresh, that the reason is the whole of
   what it has to work from, that the work is on disk, and that it must answer *that
   objection only*. Its report ends with `OUTCOME: REWRITTEN | IMPOSSIBLE` and
   `AGAINST_UNMODIFIED: FAILS | PASSES | N/A` — `N/A` whenever the leaf touched no test,
   which is every revise of green or refactor. `IMPOSSIBLE` with no `MISSING_TEST:` line is a legitimate answer, not a
   crash: the leaf says no revision can meet the objection, so the run spends no further attempt and
   **bails** at once with cause `revise-impossible`, carrying the leaf's stated reason (`Read`
   `<base directory>/BAIL.md`). The blind verifier has already rejected the state on disk, so nothing is left for it to judge.
4. **Check the prediction first (red only).** When `<phase>` is red the revise leaf rewrote
   the failing test and reported its own `PREDICTED_FAILURE:` and `PREDICTION:` lines, so run
   the same gate the Red section runs before anything reaches a verifier:
   ```
   $S/red-divergence.sh .tdd/red-prediction.md .tdd/red-run-output.txt < .tdd/revise-red-<k>.out > .tdd/verify-red.reason; echo $?
   ```
   - **Exit 1 — prediction not written before the run:** the prediction file is missing or newer than the run's output. Narrate "prediction not written before the run", not a divergence, write that line to `.tdd/verify-red.reason`, and spend attempt `k` without re-verifying, exactly as a `REJECT` does.
   - **Exit 3 — matched:** nothing was surprising; carry on to the re-verify below.
   - **Exit 0 or 2 — diverged, or a prediction nobody can read:** the rewritten test failed
     for a reason other than the one it was written to catch (exit 0), or its report carries
     no readable `PREDICTION:` line at all (exit 2), which is handled the same way. The test
     is the suspect, and verify-red is blind by construction, so spend attempt `k` **without
     re-verifying**: skip the re-verification entirely, keep the reason the script wrote to
     `.tdd/verify-red.reason` (on exit 2 write your own one-line reason there instead), mark
     it with `$S/event.sh prediction-diverged`, preserve the attempt beside that mark with
     `$S/preserve-attempt.sh <n> "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" revise-red <k> prediction-diverged` (best-effort:
     note it if it fails and carry on), and treat the attempt exactly as a `REJECT`
     does — if attempts remain, loop to attempt `k+1` with that reason; otherwise fall
     through to the budget-exhausted bail below.
   Every other phase's revise template writes no `PREDICTION:` line, so this sub-step is the
   red phase's alone.

   When `<phase>` is green, run `$S/tests-frozen.sh check --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"` here, before the re-verify.
   On tests-frozen exit 1 write a reason naming the changed file to `.tdd/verify-green.reason`, spend attempt `k`
   as a REJECT that spends REVISE_BUDGET, and launch no verifier for that attempt. On tests-frozen exit 0 the verifier is launched as before.
   On tests-frozen exit 2 the check could not answer, so **bail** as a system failure, never a REJECT, and launch no verifier.

5. **Re-verify (blind, same phase).**
   ```
   rm -f .tdd/verdict-<phase>.exit .tdd/verdict-<phase>.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-<phase> $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" --fast-cmd '<fast-cmd>' <phase> .tdd/issue-<n>-spec.md <test-path> [target] > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err
   $S/wait-leaf.sh verdict-<phase>      # foreground; on exit 3 call it again
   ```
   — overwriting the reason file, so attempt `k+1` carries the newest objection. The
   `--fast-cmd` rides along whatever the phase: green and refactor refuse to build without it
   (exit 2), red's prompt has the verifier run it once and REJECT a red that fails it for any reason
   other than the target test's expected failure, and the other phases' prompts name no fast command,
   so it changes nothing there. Both `rm
   -f`s matter in this loop: every attempt re-verifies the **same** phase, so the previous
   attempt's completion files would otherwise be read as this one's answer.
   - **PASS (exit 0):** the step is recovered. Post `### 🔎 verify-<phase> (revised) — PASS`
     with the reason, and resume the cycle from where that phase's PASS would continue.
     When `<phase>` is red, first run `$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" --red-case '<red-test-id>' <test-path>` — a revised red's PASS records the step's test files to the step's own record, as the Red section's does; tests-frozen exit 1 (the step's own Red case is gone: it names the deleted case on stdout and writes no record) is a verify-red REJECT that spends `REVISE_BUDGET`, its stdout written to `.tdd/verify-red.reason`; tests-frozen exit 2 is a bail.
   - **REJECT (exit 1):** if attempts remain, loop; otherwise fall through to the bail below.
   - **Malformed / killed-stuck (exit 2):** **bail** (system failure).

**The `diff` phase.** A REJECT on a `⟦diff-checked⟧` step runs the same loop with `<phase>`
set to `diff`, with two differences: no `step-cost.sh` line and no prediction check, since the
step has no failing test, and a re-verify that is the blind `diff` verifier rather than one
with a test path. The revise leaf is built as:
```
$S/build-develop-prompt.sh revise diff .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' .tdd/verify-diff.reason '<fast-cmd>' > .tdd/revise-diff-<k>.prompt
```
and launched as `revise-diff-<k>` like any revise leaf. The re-verify is `run-verdict.sh
--step "<STEP>" --fast-cmd '<fast-cmd>' diff <spec-file> <branch-base-sha> <step-base-sha>`, launched as `verdict-diff`
with its stdout overwriting `.tdd/verify-diff.reason`, and each `<base-sha>` is the same base sha
the original verify-diff verdict ran against — the run's branch point, and the step base sha
recorded before the step's develop-diff leaf ran, not one recorded before the revise leaf — so
the revised work is judged against the diff the rejection was about. A
recovered PASS on the `⟦diff-checked⟧` step is ticked exactly as the `⟦diff-checked⟧` PASS
bullet in *A `⟦diff-checked⟧` step* describes.

A `diff` REJECT whose reason names a pytest case as renamed and changed (#2594) launches no revise
leaf and spends no `REVISE_BUDGET` attempt. The conductor replaces the step with two steps through
`add-ledger-step.sh instead-of` — first amend the case under its old name, then rename it with the
body unchanged — and commits the plan; `add-ledger-step.sh` exit 1 bails with cause `step-too-big`.

If all `REVISE_BUDGET` attempts are still `REJECT`, the step is **not** bailed on the spot. A
criterion no blind verifier could be satisfied about in that many attempts is usually a
criterion carrying more than one behaviour — the very condition `SPLIT:` exists for — so send
one last leaf and ask it which of the two is true of this step, rather than deciding that
yourself. The reason file the last re-verify overwrote is the whole of what it is told:

```
$S/build-develop-prompt.sh exhausted .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' .tdd/verify-<phase>.reason > .tdd/develop-exhausted.prompt
rm -f .tdd/develop-exhausted.exit .tdd/develop-exhausted.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-exhausted $S/run-leaf.sh .tdd/develop-exhausted.prompt --permission-mode bypassPermissions > .tdd/develop-exhausted.out 2> .tdd/develop-exhausted.err
$S/wait-leaf.sh develop-exhausted   # foreground; on exit 3 call it again
```

That leaf answers in prose around its report lines, so **read its answer with the script, not
by eye** — which outcome it holds is an exit code, never a judgement made per run:

```
$S/exhausted-outcome.sh < .tdd/develop-exhausted.out > .tdd/exhausted-answer.txt; echo $?
```
**exit 0** is the split, **exit 1** the step needs the user and is parked, **exit 3** neither
answer. Each is a branch of its own:

- **exit 0 — split.** `.tdd/exhausted-answer.txt` holds the criteria the leaf named, one per
  line, and they **replace** the step nothing could satisfy rather than queue ahead of it —
  the criterion itself was what was wrong. Restore the tree first, since the step's rejected
  work is uncommitted and would otherwise become the first replacement step's inherited
  start, then grow the plan in **one** call and commit it:
  ```
  git reset --hard HEAD
  git clean -f -- <test-path>   # a test file Red created is untracked, so the reset leaves it
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$step" added=<count>
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-split at=exhausted anchor="$step" added=<count>
  $S/add-ledger-step.sh .tdd/issue-<n>.md instead-of "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<criterion>' …   # every line of the answer in ONE call
  git add -A && git commit -m "plan: replace <STEP summary> with <count> smaller steps (#<n>)"
  ```
  The marks go first for the reason the Green split's do: they read the title out of the
  ledger, and `instead-of` takes the step out of it (#437). Like every split, the call passes
  no `--criterion`: a split keeps its anchor's criterion, because it is the same behaviour
  broken smaller. The `at=exhausted` is what tells this split apart from a Green leaf's volunteered
  one: both grow the plan through `add-ledger-step.sh` and both write `step-added` and
  `step-split`, so without it a log reader cannot say whether the plan grew because a leaf
  asked or because the budget ran out — and those are different facts about the run.
  Then loop back to `next-unchecked.sh`, which now hands over the first of them. The ledger is
  committed before the run goes on because the committed ledger is what a resumed run reads:
  uncommitted, the replacement steps are lost and the step that could not be satisfied is
  handed out again. **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`**, exactly
  as a Green leaf's volunteered split does when it meets
  `VERI_STEP_GROWTH`: the criteria are filed under `## Owed steps` and the plan is unchanged (see `<base directory>/BAIL.md`).
  **`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
- **exit 1 — the step needs the user.** `.tdd/exhausted-answer.txt` holds the leaf's answer:
  the criterion is wrong, contradicts another, or needs a decision this run has no authority
  to make. **Park the step** — stop the run there, carrying that answer and the verifier's
  last rejection reason (`.tdd/verify-<phase>.reason`), and leave the plan as it is so the
  user's decision picks the run back up. Post a `### ⏸️ Parked — <phase> (needs the user)`
  comment carrying `.tdd/exhausted-answer.txt` verbatim and that rejection reason, so what the
  user has to decide about is on the thread they already read rather than in a leaf log inside
  a worktree. This is a deliberate escalation, not a failure to split, so it carries a mark of
  its own rather than the split's or the bail's — it is the one outcome that stops the run
  without bailing it, and a log holding neither reads as a run that stopped saying nothing:
  ```
  step="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-escalated anchor="$step"
  ```
- **exit 3 — neither answer.** The leaf volunteered no split and asked for no decision, so
  there is nothing new to act on: **bail the step** with cause `revise-exhausted` as a
  **process** failure (the methodology could not satisfy the blind verifier within budget),
  recording the **last rejection reason** — exactly the stop this section took before the
  leaf above existed.

A **supervisor exit 2** on that leaf is a bail like any other developer leaf's
(`killed-stuck`, a system failure): nothing answered, so no outcome was reported.

`REVISE_BUDGET` (verdict axis) is **independent** of the supervisor's `VERI_STUCK_RETRIES`
(liveness axis) and of `VERI_REFACTOR_BUDGET` (cost axis): the first governs a leaf that
finished with a bad verdict, the second a leaf that never produced one, the third how many
transforms one step's tidying is worth. A `REJECT` is veri working as designed — the blind verifier
refusing to rubber-stamp — so the bounded revise is a *correction*, never an excuse to keep
hammering past the budget.

