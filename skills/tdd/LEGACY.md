   A **legacy** run — the spec carries the `## Legacy` section `capture-spec.sh` writes for the
   `legacy` label, an issue never also labelled `refactor` — wraps code no test covers before
   anyone refactors it. Its phases run in order **Seam → Surround → Verify**: confirm that a
   seam drives the region, surround the region with black-box tests driven through that seam,
   then verify them.

   **Planning.** Each plan step names one **region**, a file and a symbol or line range, and one
   **seam**, a command or callable outside the region that drives it (an entry-point CLI, an
   exported function, an HTTP handler), and lists `⟦phases: seam,surround⟧`. The plan verifier
   rejects a step naming no region, no seam, or a seam inside its own region. The phase list
   written at plan time is what a resume reads.

   **Who runs a legacy step.** This file runs it, not `PHASED.md`, although the step lists
   `⟦phases: …⟧`. A legacy step is never run through a fused call of PRD 027 (#4026–#4029): each of
   its leaves is launched by the conductor through `supervise.sh` and waited on as *Launching a
   leaf* sets out.

   **Seam.** For each step whose next phase (`$S/ledger-steps.sh next-phase < .tdd/issue-<n>.md`)
   is `seam`, launch one `develop-seam` leaf through `supervise.sh`, its prompt built by
   `$S/build-develop-prompt.sh seam <spec-file> "<STEP>" '<test-cmd>'`. The leaf writes no test and
   edits no file. If `git status --porcelain` prints anything once it exits, refuse to continue —
   stop the run, as after a cover leaf. Read its report through
   `$S/seam-outcome.sh < .tdd/develop-seam.out`:
   - exit 0, `REACHES: yes`: record it with
     `$S/tick-ledger.sh --phase seam .tdd/issue-<n>.md "<STEP>"` and commit the ledger, so a
     resumed run does not confirm the seam twice;
   - exit 1, `REACHES: no`: the first time for this region, do not bail: run **Break** below,
     keeping the reason `seam-outcome.sh` printed. After a `verify-break` PASS, launch
     `develop-seam` again; a second `REACHES: no` **bails with cause `no-seam`**, a process
     failure, its note carrying both leaves' reasons, the first seam leaf's and the second's
     (`Read` `<base directory>/BAIL.md`);
   - exit 2, no readable answer: **bail** as a system failure (`no-verdict`) (`Read`
     `<base directory>/BAIL.md`).

   **Break.** A region whose seam does not reach it gets **at most one** dependency-breaking edit,
   and only one from this catalogue; no other edit is allowed:
   - **`sprout`**: the region's code moved unchanged into a new function or class that the old
     code now calls and a test can call directly;
   - **`extract and override`**: a dependency call extracted into a method a test may override.
   Record `git rev-parse HEAD` as the break's base sha and launch one `develop-break` leaf for the
   region through `supervise.sh`, its prompt built by
   `$S/build-develop-prompt.sh break <spec-file> "<STEP>" '<test-cmd>'`: it applies one catalogued
   edit, names it on a `BREAK:` line, commits it and reports the seam it made. After its wait exits
   0, `$S/suite-reported.sh develop-break` runs as `PHASED.md` sets out for a phase leaf. No test
   exists to move, so `$S/transform-touches-tests.sh <base-sha>` exit 1 on the break commit
   rejects it before any verifier is launched, and exit 2 is no answer; the existing suite is the only net, so the fast tier and
   the affected suites must stay green. Then launch one `verify-break` leaf through
   `supervise.sh`, named `verdict-break` as *Launching a leaf* sets out:
   `run-verdict.sh --step "<STEP>" --fast-cmd '<fast-cmd>' break .tdd/issue-<n>-spec.md <region-file> <base-sha>`.
   The blind verifier reads `git diff <base-sha>..HEAD`, never the developer's report.
   - PASS: launch `develop-seam` again, as **Seam** says.
   - REJECT, or `transform-touches-tests.sh` exit 1: revise under `REVISE_BUDGET` like any other
     reject, `break` being the phase revised (`Read` `<base directory>/REVISE.md`).
   - `transform-touches-tests.sh` exit 2, or no verdict once `verify.sh` has relaunched the leaf
     `VERI_NO_VERDICT_RETRIES` times: **bail** as a system failure (`no-verdict`) (`Read`
     `<base directory>/BAIL.md`).

   **Surround.** Once every legacy step's seam is confirmed, the run goes on to Surround. For each
   step whose next phase is `surround`, record `git rev-parse HEAD` as its base sha and launch one
   `develop-surround` leaf through `supervise.sh`, its prompt built by
   `$S/build-develop-prompt.sh surround <spec-file> "<STEP>" '<test-cmd>'`: it commits
   characterization tests that drive the region only through the seam, and edits no production
   file. Each `MUTATION:` criterion of the spec, the criteria `coverage-blocker.sh` writes into the
   legacy issue a refusing refactor files, is a row `develop-surround` owes in its step's mutant
   table, beside the rows it proposes. After its wait exits 0, `$S/suite-reported.sh develop-surround` runs as `PHASED.md` sets
   out for a phase leaf. Then launch one `verify-surround` leaf through `supervise.sh`, named
   `verdict-surround` as *Launching a leaf* sets out:
   `run-verdict.sh --step "<STEP>" surround .tdd/issue-<n>-spec.md <test-path>`, `<test-path>` being
   the leaf's `TEST_PATH:`. The blind verifier takes the `pin` phase's inputs and never the
   developer's report. `VERI_SKIP_VERIFY` never skips `surround`: a run naming it exits 2 at
   launch.
   - PASS: the region is not yet surrounded. Run
     `$S/surround-mutants.sh <develop-report> .tdd/verify-surround.reason -- <command>`, where
     `<develop-report>` is the step's `develop-surround` report (a revise keeps its table: the
     mutants target production code, which no revise edits), and `<command>` runs
     each test file the step's Surround commit added (`git diff --name-only --diff-filter=A
     <base-sha> HEAD`) through the repo's `veri: one test file:` command
     (`$S/detect-test-command.sh --tier "one test file"`, `"$1"` being the file), or once through
     the all tier when the repo declares none. Route its exit:
     - 0, every mutant red: record it with
       `$S/tick-ledger.sh --phase surround .tdd/issue-<n>.md "<STEP>"` and commit the ledger;
       `next-phase` then exits 3, so the step reads as done.
     - 1 with a `survived` row: revise it as a REJECT, the script's output as the reason,
       spending `REVISE_BUDGET`.
     - 1 ending `short <k> of <N>`: run
       `$S/tick-ledger.sh --surround-short .tdd/issue-<n>.md "<STEP>"`, which records the step's one
       free relaunch on its ledger line. On exit 0 commit the ledger, then relaunch
       `develop-surround` once to add rows, spending no `REVISE_BUDGET`, then verify-surround and
       this run again. On exit 1 the relaunch was already spent, by this run or by the run a resume
       carries on: **bail with cause `surround-short`**, a process failure (`Read`
       `<base directory>/BAIL.md`); on exit 2, **bail** as a system failure (`no-verdict`)
       (`Read` `<base directory>/BAIL.md`).
     - 2: **bail** as a system failure (`no-verdict`) (`Read` `<base directory>/BAIL.md`).
   - REJECT: revise under `REVISE_BUDGET` like any other reject, `surround` being the phase
     revised (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`).
   - No verdict: `verify.sh` relaunches the leaf up to `VERI_NO_VERDICT_RETRIES` times; once
     spent, **bail** as a system failure (`no-verdict`) (`Read` `<base directory>/BAIL.md`).
   verify-surround adds no budget of its own; the rows a mutant table owes are
   `VERI_SURROUND_MUTANTS`, a budget on an axis of its own, never folded into `REVISE_BUDGET`.

   **After the run is done.** Once `DRAFT-PR.md` sub-step 4 has made the ✅ Done comment (or
   `run-done.sh` has, where it makes that comment), run `$S/release-covered.sh <n>`: when this
   issue is the coverage issue a refusing refactor filed, it releases the bailed refactor issue
   it blocks, so that issue is taken again once this one closes. Exit 0 (released) and exit 3
   (nothing to release) go on; exit 2 is reported in the run's final report and is not a bail,
   since the run is already done.
