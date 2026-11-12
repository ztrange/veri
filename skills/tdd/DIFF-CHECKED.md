## A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)

A `⟦diff-checked⟧` step runs no Red leaf, and no Green or Refactor phase either: its
criterion is a property of the branch's own diff, so there is no failing test to write and
its step adds none. On a fresh run and on a resume alike, the step base sha is the last
commit that changed the ledger — the previous step's tick — never a `HEAD` taken after a
killed `develop-diff` attempt's commit: record it with `git log -1 --format=%H -- .tdd/issue-<n>.md` before the `develop-diff` leaf
runs. On a fresh step, `git rev-parse HEAD` taken before the `develop-diff` leaf runs names
that same commit, since every step ends in a ledger commit; on a resume it may not. That leaf, built by `build-develop-prompt.sh diff <spec-file>
"<STEP>" '<test-cmd>' '<fast-cmd>'`, makes the change the criterion names — or makes no
commit, when the criterion is that something stays unchanged — and keeps the fast tier and
then the affected suites green before it reports. Then the blind `diff` verifier,
`run-verdict.sh --step "<STEP>" --fast-cmd '<fast-cmd>' diff <spec-file> <branch-base-sha> <step-base-sha>`, runs the fast tier and then the affected suites, rejecting the step when
either is red, and judges it against the run's branch point, `git merge-base HEAD
origin/<default>`, and its own diff from the step base sha. Both are launched through the supervisor and waited on as
*Launching a leaf* sets out, the leaf as `develop-diff` and the verifier as `verdict-diff`.

A supervisor exit 2 on the `develop-diff` leaf is a `killed-stuck` bail, as for any developer
leaf (see `<base directory>/BAIL.md`). After its wait exits 0 and before the verifier is launched, run `$S/suite-reported.sh develop-diff`:
exit 2 means the leaf left no `SUITE:` line, so launch no verifier and **bail** as a system
failure with cause `report-missing` (`Read` `<base directory>/BAIL.md`). The `diff` revise leaf asks for the line too, so after its wait
exits 0 the same check, `$S/suite-reported.sh revise-diff-<k>` for the `revise-diff-<k>` leaf, runs
before the re-verify with the same exit 2 outcome. After the `develop-diff` leaf's wait exits 0, and after each
`revise-diff-<k>`, before its verifier, run `$S/diff-leaf-deviation.sh <leaf> <step-base-sha> .tdd/issue-<n>.md`.
Exit 0 means a deviation was found and recorded as a `diff-leaf-deviation` event; exit 3 means the one-commit
flow, or no commit for an unchanged criterion. Both go on to the verifier. Exit 2 **bails** the run. Never
reset, squash or repair the leaf's commits.

The `develop-diff` leaf's commit, and each `revise-diff-<k>` leaf's, are the step's work: leave
each as made, and run no `git reset --soft`, squash or re-commit on it. After a PASS the
ledger tick is committed as its own commit on top of the leaf's commit, so a step that
changed something leaves the leaf's commit and then the tick commit, in that order.

The verifier's verdict closes the `⟦diff-checked⟧` step:

- **PASS (exit 0):** first run `$S/pin-recheck.sh <step-base-sha>` against the step base sha,
  its work being committed by now, and read its exit as the Refactor loop's PASS reads it, a
  pin that stayed green, or a before-state pin this range disarmed (a stale one, green on the base too, is printed `stale: <record file> <test path>`, or `<mutated file>` for a mutation pin, and is no REJECT), being a REJECT of this step that spends `REVISE_BUDGET`; a pin whose own tested file is gone (a before record included, whose named test file the range deletes) or whose mutated file the range deletes is printed as `retired:` and is not a REJECT (exit 3 when every selected pin is retired); a before-state pin's replay path gone before the range is skipped and the pin still runs. The tick below refuses (exit 2) without the receipt that exit 0 or 3 leaves. Then tick the `⟦diff-checked⟧` step with `tick-ledger.sh` — without
  `--refactor-pending`, since no refactor loop follows — commit the ledger and push it as
  Green does, post `### ✅ Step done` by running `$S/comment.sh <n> step-done`, composing none of it, then tick its criterion in the issue body with `tick-issue-criterion.sh` on
  `criterion-finished.sh` exit 0, ticking nothing on exit 3, exactly as a Refactor loop's
  PASS does.
- **REJECT (exit 1):** a revise of the `⟦diff-checked⟧` step's `develop-diff` work under
  `REVISE_BUDGET` — when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`. On a recovered PASS tick as above, on
  budget-exhausted **bail** (`Read` `<base directory>/BAIL.md`).
- **Malformed / killed-stuck (exit 2):** no verdict on the `⟦diff-checked⟧` step could be
  obtained, so **bail** as a system failure (`no-verdict`) — see `<base directory>/BAIL.md`.

A `⟦fixture-repair⟧` step's verify-green PASS closes it the same way: ticked with
`tick-ledger.sh` without `--refactor-pending`, committed with a `test:` subject, no Refactor
loop run, and its criterion ticked with `tick-issue-criterion.sh` on `criterion-finished.sh`
exit 0, ticking nothing on exit 3, as a `⟦diff-checked⟧` PASS does.

