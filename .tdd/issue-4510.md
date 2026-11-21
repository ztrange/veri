# Plan for #4510 — step-close.sh takes a re-pin plan commit as the green sha, and run-step.sh closes the refactor-pending step before the inserted re-pin step runs

- [x] step-close.sh passes the refactor-pending step's own green commit (the commit that marked it refactor pending) to graded-changed.sh, pin-recheck.sh (base `<green>~1`) and tests-frozen.sh rerecord-refactored when a later plan commit only added a `⟦diff-checked⟧ ⟦added⟧` re-pin step to the ledger ⟦criterion 1⟧
- [x] run-step.sh runs an open `⟦diff-checked⟧` step the ledger holds after the refactor-pending step (diff-step.sh) ahead of that step's refactor-half and step-close ⟦criterion 2⟧
- [x] SCRIPTS.md's step-close.sh and run-step.sh entries state the green commit and the re-pin step's precedence
