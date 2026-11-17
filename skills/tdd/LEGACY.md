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

   **Surround is owed.** The Surround phase does not exist yet (PRD 031.1b). Once every legacy
   step's next phase is `surround`, **bail with cause `surround-owed`**, a process failure: the
   `### ⛔ Bailed` note lists each step's region and its confirmed seam, read from the ledger.
   The ledger, the branch and the draft PR stay, so `release-issue.sh <n>` and a resume carry on
   from the ledger (`Read` `<base directory>/BAIL.md`).
