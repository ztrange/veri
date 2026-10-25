   Then run the issue's **one structural pass**, once, before the PR is readied: the
   structural candidates the steps recorded rather than applied, each taken up by one
   `structural` transform leaf, bounded to every file the issue touched plus the files the
   candidate names, and counted against the issue's budget, not a step's. The conductor runs the pass whenever
   `refactor-owed.sh list` prints a candidate, and never skips or shortens it for cost: the
   way to spend less is to set a lower `VERI_ISSUE_REFACTOR_BUDGET` before launch. A run does
   a refactor now, or drops it: the pass never files one. Every candidate it does not apply is
   recorded with `refactor-owed.sh not-done` and its reason, and `render` shows it under
   `### Not done` in the PR body:
   ```
   git merge-base HEAD origin/<default>                 # → <issue-base>
   $S/refactor-owed.sh list .tdd/issue-<n>-refactor-owed.md   # one candidate per line; exit 3 ⇒ no pass
   ```
   A candidate recorded test-only is never listed, so it launches no predicate or
   transform leaf; `render` still shows it under `### Test-only` in the PR body.
   An out-of-scope candidate is listed like any other.
   For each candidate, in the order `refactor-owed.sh list` prints them — most valuable first —
   `<count>` being the transforms the pass has already landed:
   ```
   $S/refactor-budget.sh --issue <count>   # exit 0 ⇒ launch; exit 3 ⇒ the pass is over
   git rev-parse HEAD                      # → <base-sha>
   $S/refactor-touched.sh --issue <issue-base> --candidate '<candidate>'   # → <bound>
   ```
   A candidate the budget stops is recorded, with every candidate after it:
   ```
   $S/refactor-owed.sh not-done .tdd/issue-<n>-refactor-owed.md '<candidate>' budget-spent
   ```
   Before its transform leaf, a `develop-cover` leaf, prompted by `build-develop-prompt.sh cover`
   with the spec, the candidate and the test command, mutates the code the candidate will move, runs the suites,
   expects red and restores. Read its report through `$S/cover-outcome.sh`: exit 2 bails as a
   **system** failure (`no-verdict`) (`Read` `<base directory>/BAIL.md`). Exit 3 — `COVERED: unreachable` or `type-only` — goes on;
   exit 1, `COVERED: no`, launches no transform: the candidate is recorded `uncovered`, and the
   run neither bails nor files anything:
   ```
   $S/refactor-owed.sh not-done .tdd/issue-<n>-refactor-owed.md '<candidate>' uncovered
   ```
   This is where each candidate's predicate comes from: after a covered candidate, a
   predicate leaf, prompted by `build-develop-prompt.sh predicate` with the spec, the
   candidate, the test command and `<bound>`, and launched through the supervisor as `develop-predicate`, reports one
   `PREDICATE:` line, which the conductor checks and records:
   ```
   $S/structural-predicate.sh .tdd/issue-<n>-predicate < <leaf-report>   # exit 0 ⇒ recorded; 1 ⇒ already applied; 3 ⇒ skip
   ```
   That record is the test path the transform verifier runs, in place of the prose
   candidate. A candidate with no predicate is skipped — only exit 3, for
   `PREDICATE: NONE`, is recorded with `refactor-owed.sh not-done` and `no-predicate`
   rather than handed to a transform leaf; exit 1, a command already
   true, means the candidate is already applied, and it is recorded as applied below
   without a transform leaf; exit 2 is no answer and **bails** as a **system** failure (`no-verdict`, see `<base directory>/BAIL.md`).
   Each transform leaf's prompt is `build-develop-prompt.sh structural`'s, handed the spec, the candidate as
   `list` printed it, the test command and `<bound>`, written to
   `.tdd/develop-structural.prompt`; the leaf is launched through the supervisor as
   `develop-structural`. After its wait exits 0 and before its commits are checked, run
   `$S/suite-reported.sh develop-structural`: exit 2 means the report carries no `SUITE:` line,
   so launch no transform verifier and **bail** as a system failure with cause `report-missing` (`Read` `<base directory>/BAIL.md`).
   An out-of-bounds skip — the leaf left the tree as it found it and said so — is exempt: it
   keeps its main outcome, a transform `REJECT` and the next candidate (a process outcome),
   never a `report-missing` bail. Its commits are checked with
   `$S/transform-touches-tests.sh <base-sha> <bound>` — exit 1 rejects the transform (a test file,
   or a file outside `<bound>`), exit 2 is no
   answer — then judged by the long
   refactor's blind `transform` verifier against `<base-sha>`, one commit per transform —
   both before the next candidate's leaf is launched. A `REJECT`, or a transform `transform-touches-tests.sh` rejected, resets to `<base-sha>`, records the
   candidate `transform-rejected` with `refactor-owed.sh not-done`, and moves on to the next candidate.
   ```
   rm -f .tdd/verdict-transform.exit .tdd/verdict-transform.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-transform $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" transform .tdd/issue-<n>-spec.md .tdd/issue-<n>-predicate <base-sha> > .tdd/verify-transform.reason 2> .tdd/verify-transform.err
   $S/wait-leaf.sh verdict-transform   # foreground; on exit 3 call it again
   ```
   A `PASS` records the candidate as applied, with the commit that applied it, so `render`
   lists it as applied rather than owed; a candidate `structural-predicate.sh` exited 1 for
   launches no transform leaf and is recorded the same way, at the current HEAD; the fourth argument is the applying commit's subject, which `render` prints beside the sha:
   ```
   $S/refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md '<candidate>' "$(git rev-parse HEAD)" "$(git log -1 --format=%s)"
   git add .tdd/issue-<n>-refactor-owed.md
   git commit -m "chore: record the structural pass's applied candidate (#<n>)"
   ```
   Every `refactor-owed.sh not-done` call above (`budget-spent`, `uncovered`, `no-predicate`,
   `transform-rejected`) is followed at once, before the next candidate's leaf is launched, by
   staging and committing the owed file, so a later candidate's `REJECT` reset to its `<base-sha>`
   keeps the row:
   ```
   git add .tdd/issue-<n>-refactor-owed.md
   git commit -m "chore: record the structural pass's not-done candidate (#<n>)"
   ```
   Once the pass ends — the candidates run out, or the budget is spent — mark it once, with
   the transforms it landed, its budget and why it stopped. `stopped=` takes only
   `candidates-done`, `budget-spent` or `nothing-structural`, and `budget-spent` is marked
   only when `refactor-budget.sh --issue` exited 3, i.e. `transforms` equals the budget:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh structural-pass transforms=<count> budget=<VERI_ISSUE_REFACTOR_BUDGET> stopped=<reason>
   ```
