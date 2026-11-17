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
   - exit 1, `REACHES: no`: **bail with cause `no-seam`**, a process failure, carrying the
     leaf's reason that `seam-outcome.sh` printed (`Read` `<base directory>/BAIL.md`);
   - exit 2, no readable answer: **bail** as a system failure (`no-verdict`) (`Read`
     `<base directory>/BAIL.md`).

   **Surround.** Once every legacy step's seam is confirmed, the run goes on to Surround. For each
   step whose next phase is `surround`, record `git rev-parse HEAD` as its base sha and launch one
   `develop-surround` leaf through `supervise.sh`, its prompt built by
   `$S/build-develop-prompt.sh surround <spec-file> "<STEP>" '<test-cmd>'`: it commits
   characterization tests that drive the region only through the seam, and edits no production
   file. After its wait exits 0, `$S/suite-reported.sh develop-surround` runs as `PHASED.md` sets
   out for a phase leaf. Then launch one `verify-surround` leaf through `supervise.sh`, named
   `verdict-surround` as *Launching a leaf* sets out:
   `run-verdict.sh --step "<STEP>" surround .tdd/issue-<n>-spec.md <test-path>`, `<test-path>` being
   the leaf's `TEST_PATH:`. The blind verifier takes the `pin` phase's inputs and never the
   developer's report. `VERI_SKIP_VERIFY` never skips `surround`: a run naming it exits 2 at
   launch.
   - PASS: record it with `$S/tick-ledger.sh --phase surround .tdd/issue-<n>.md "<STEP>"` and
     commit the ledger; `next-phase` then exits 3, so the step reads as done.
   - REJECT: revise under `REVISE_BUDGET` like any other reject, `surround` being the phase
     revised (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`).
   - No verdict: `verify.sh` relaunches the leaf up to `VERI_NO_VERDICT_RETRIES` times; once
     spent, **bail** as a system failure (`no-verdict`) (`Read` `<base directory>/BAIL.md`).
   Surround adds no budget of its own.
