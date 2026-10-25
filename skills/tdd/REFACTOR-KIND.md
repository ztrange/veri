   A **refactor-kind** run — the spec carries the `## Refactor` section `capture-spec.sh`
   writes for the `refactor` label — changes no behaviour, so it has no failing test to plan
   around. Plan each step that is neither `⟦diff-checked⟧` nor a pin step as one named
   refactoring whose criterion is a shell predicate, false before the step and true after it:
   the smell being present is the step's Red. The plan verifier REJECTs such a step not
   written that way; a test-only step is REJECTed only when it is planned as anything but
   `⟦diff-checked⟧` or a pin step. A refactor-kind plan may mix refactoring steps with
   `⟦diff-checked⟧` or pin steps for its test-only criteria. In a
   refactor-kind plan, fold a deletion into the step that makes the code dead: never leave a
   no-op in place for a later step to delete, whose Cover would run on code nothing reaches.
   Each refactoring step opens with a cover leaf, which mutates the code the step will move, runs the suite,
   expects red, restores and reports `COVERED:` and `CAUGHT_BY:`. If
   `git status --porcelain` prints anything once it exits, refuse to continue — stop the
   run: the transform would otherwise commit the leftover mutation as a refactoring.
   Read its report through `$S/cover-outcome.sh`: exit 2 bails as a **system** failure
   (`no-verdict`) (`Read` `<base directory>/BAIL.md`). Exit 3 — `COVERED: unreachable` or `type-only` with its `PROOF:` — goes
   on to Transform without bailing or running `coverage-blocker.sh`, posting the proof it
   prints in the step's Cover comment, and for a `type-only` step saves to
   `.tdd/issue-<n>-proof` the text `cover-outcome.sh` printed after `type-only: ` — the
   proof command the transform is checked against; exit 1, `COVERED: no`, refuses the step:
   **bail with cause `uncovered`**, narrating the remedy —
   find a seam and surround the behaviour with tests first — and run
   `$S/coverage-blocker.sh <n>`, which files the coverage issue and blocks this one on it,
   so the queue cannot retake it only to refuse again (`Read` `<base directory>/BAIL.md`).
   A refactor-kind step therefore runs **Cover → Transform → Verify**, not Red → Green →
   Refactor, unless it is `⟦diff-checked⟧`, which runs develop-diff then verify-diff and never
   Cover or Transform. After Cover, a transform leaf applies the step's one named refactoring and
   commits it; after its wait exits 0 and before the transform verifier is launched, run
   `$S/suite-reported.sh develop-transform`: exit 2 means the report carries no `SUITE:` line,
   so launch no verifier and **bail** as a system failure with cause `report-missing` (`Read` `<base directory>/BAIL.md`). Then
   `$S/transform-touches-tests.sh <base-sha>` reads every commit since the
   step's base sha, and exit 1 rejects the transform — a refactoring that edits a test file
   has moved the goalposts — while exit 2 is no answer. After the transform commits, the
   conductor itself — not a leaf — reruns a `type-only` step's saved proof command in
   `.tdd/issue-<n>-proof`: a non-zero exit rejects the transform as
   `transform-touches-tests.sh` exit 1 does. The blind `transform` verifier reads
   the diff from the same base sha. An abandoned refactor-kind step has no untracked test to
   clean — its transform commits are the work — so it is abandoned by resetting to its base
   sha, `git reset --hard <base-sha>`.
