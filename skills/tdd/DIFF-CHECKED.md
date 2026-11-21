## A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)

Run `$S/run-step.sh <n>`, again on exit 3, and on 1 or 2 go on by the paragraph its last line names: it
runs `diff-step.sh`, this section in one call. `diff-step` by hand ends `$S/step-tick.sh <n>`.

A `⟦diff-checked⟧` step runs no Red leaf, and no Green or Refactor phase either: its
criterion is a property of the branch's own diff, so there is no failing test to write and
its step adds none. On a fresh run and on a resume alike, the step base sha is the last
commit that changed the ledger — the previous step's tick — never a `HEAD` taken after a
killed `develop-diff` attempt's commit: record it with `git log -1 --format=%H -- .tdd/issue-<n>.md` before the `develop-diff` leaf
runs. On a fresh step, `git rev-parse HEAD` taken before the `develop-diff` leaf runs names
that same commit, since every step ends in a ledger commit; on a resume it may not. That leaf, built by `build-develop-prompt.sh diff <spec-file>
"<STEP>" '<test-cmd>' '<fast-cmd>'`, makes the change the criterion names — or makes no
commit, when the criterion is that something stays unchanged — and keeps the fast tier and
then the test files covering the changed files green before it reports, never running the `affected` tier. Then the
blind `diff` verifier, `run-verdict.sh --step "<STEP>" --fast-cmd '<fast-cmd>' --branch-base <base> diff <spec-file> <step-base-sha>`, runs the fast tier and then the test files covering the changed files, never the `affected`
tier, rejecting the step when either is red, and judges it against the run's recorded branch base `<base>`
(`.tdd/issue-<n>-branch-base` in the main working tree, never a remote-tracking ref, which a leaf can rewrite) and its own diff from the step base sha. Both are launched through the supervisor and waited on as
*Launching a leaf* sets out, the leaf as `develop-diff` and the verifier as `verdict-diff`.
**Switched off:** with `diff` in `.tdd/issue-<n>-skip-verify`, no verifier launches: record
`VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh verify-diff-skipped reason=switched-off`,
write `skipped` to `.tdd/verdict-diff.exit`, and take the PASS branch below, `pin-recheck.sh`
first. The leaf, `suite-reported.sh` and `diff-leaf-deviation.sh` still run before it.

A supervisor exit 2 on the `develop-diff` leaf is a `killed-stuck` bail, as for any developer
leaf (see `<base directory>/BAIL.md`). After its wait exits 0 and before the verifier is launched, run `$S/suite-reported.sh develop-diff 2> .tdd/suite-reported.err`:
exit 2 means the leaf left no `SUITE:` line, so launch no verifier; if `$S/adjudicate.sh left <n>` exits 0, launch `adjudicate-report-missing` through `supervise.sh` with `.tdd/suite-reported.err` as the stderr file, its prompt built by `$S/build-adjudicate-prompt.sh <n> report-missing 2 .tdd/suite-reported.err suite-reported.sh develop-diff` (`Read` `<base directory>/ADJUDICATE.md`); on that `left` call's exit 3, or on any answer, `retry` included, **bail** as a system failure with cause `report-missing`, with no verifier, no second `suite-reported.sh` call and no relaunch, the bail event written by `BAIL.md`'s step 3 command with that cause, never a line guarded by a shell variable (`Read` `<base directory>/BAIL.md`). The `diff` revise leaf asks for the line too, so after its wait
exits 0 the same check, `$S/suite-reported.sh revise-diff-<k> 2> .tdd/suite-reported.err` for the `revise-diff-<k>` leaf, runs
before the re-verify with the same exit 2 outcome, its adjudication included, `revise-diff-<k>` in place of `develop-diff` as the prompt's command. After the `develop-diff` leaf's wait exits 0, and after each
`revise-diff-<k>`, before its verifier, run `$S/diff-leaf-deviation.sh <leaf> <step-base-sha> .tdd/issue-<n>.md`.
Exit 0 means a deviation was found and recorded as a `diff-leaf-deviation` event; exit 3 means the one-commit
flow, or no commit for an unchanged criterion. Both go on to the verifier. Exit 2 **bails** the run. Never
reset, squash or repair the leaf's commits.

The `develop-diff` leaf's commit, and each `revise-diff-<k>` leaf's, are the step's work: leave
each as made, and run no `git reset --soft`, squash or re-commit on it. After a PASS the
ledger tick is committed as its own commit on top of the leaf's commit, so a step that
changed something leaves the leaf's commit and then the tick commit, in that order.

The verifier's verdict closes the `⟦diff-checked⟧` step:

- **The flip of a `⟦test-quality⟧` step.** Such a step fixes one test case (`<base directory>/DRAFT-PR.md`),
  and the conductor, not the verifier, proves the fix live. After its verify-diff PASS (or
  `skipped`) and before anything below, read the last `FLIP: <test file> '<old>→<new>'` line of the
  report of the leaf that made the step's last commit (`.tdd/develop-diff.out`, or the last
  `revise-diff-<k>` leaf's), and run
  `$S/mutation-probe.sh <test file> '<old>' '<new>' -- <command…>`, `<command…>` the repo's
  `veri: one test file:` command run on that test file,
  `alone="$($S/detect-test-command.sh --tier "one test file")"` then `sh -c "$alone" sh <test file>`,
  or, when the repo declares none (that call exits 3), its all-tier command,
  `all="$($S/detect-test-command.sh --tier all)"` then `sh -c "$all"`. Exit **0** (the flipped case
  went red) goes on to the PASS branch below. The call sets no `VERI_MUTATION_RECORD`, so the probe
  writes no `.tdd/issue-<n>-mutations.md` record: the flip proves the fix once, and nothing replays it. Exit **1** (it stayed green) is a verify-diff REJECT naming the
  test file, spending `REVISE_BUDGET`: write `REJECT: flipping <old>→<new> in <test file> left <test file> green`
  to `.tdd/verify-diff.reason` (`Read` `<base directory>/REVISE.md`); a report with no `FLIP:` line, or one not of that form, is a
  REJECT the same way, its reason saying the line is missing. Exit **2**, or a `detect-test-command.sh` exit 2, bails `no-verdict`, a
  system failure (`Read` `<base directory>/BAIL.md`).
- **PASS (exit 0):** first run `$S/pin-recheck.sh --branch-base <base> <step-base-sha>` against the step base sha, `<base>` the recorded branch base (on a re-pin step, the one `pin-reject-route.sh --recheck` adds, against `<green>~1` instead, `<green>` the ledger's last commit before the step base, the re-armed step's green tick, so the range holds the fix that disarmed the pin),
  its work being committed by now, and read its exit as the Refactor loop's PASS reads it, a
  pin that stayed green, or a before-state pin this range disarmed (a stale one, green on the base too, is printed `stale: <record file> <test path>`, or `<mutated file>` for a mutation pin, and is no REJECT), being a REJECT of this step that spends `REVISE_BUDGET`; a pin whose own tested file is gone (a before record included, whose named test file the range deletes) or whose mutated file the range deletes is printed as `retired:` and is not a REJECT (exit 3 when every selected pin is retired); a before-state pin's replay path gone before the range is skipped and the pin still runs. The tick below refuses (exit 2) without the receipt that exit 0 or 3 leaves. Then tick the `⟦diff-checked⟧` step with `tick-ledger.sh` — without
  `--refactor-pending`, since no refactor loop follows — commit the ledger as `chore: diff-checked — <step summary> (#<n>)` and push it as
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

A `⟦lint-repair⟧` step, the one `DRAFT-PR.md` appends on a red lint, runs as any
`⟦diff-checked⟧` step does. Its verify-diff prompt carries the repo's declared lint command
(the `veri: lint:` line of its CLAUDE.md), which the verifier runs, rejecting while it exits
non-zero.
