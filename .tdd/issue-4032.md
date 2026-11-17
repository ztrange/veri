# Plan for #4032 — PRD 027.10: readying the PR and its first CI wait is one call

- [x] `pr-ready-wait.sh <n>` follows the port convention and refuses no argument and a missing preflight with exit 2 before any inner call ⟦criterion 9⟧
- [x] it reads the PR url (empty exits 2), checks the tree, runs `pr-ready.sh` and `wait-ci.sh`, settles `pr_url`, `pr_number`, `ci=green` and `no_checks=1`, and stops at the first call that is not clean ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧
- [x] a wait whose slice runs out exits 3 and a second call only waits again; its wait record names its conductor ⟦criterion 4⟧
- [x] a guard fails when an inner call is a `$S/` script sub-step 2's first block does not name, and the PR is readied and waited on through a stub `gh` for real ⟦criterion 10⟧
- [x] docs: `DRAFT-PR.md` sub-step 2's first block, `SCRIPTS.md`, rows and grades ⟦criterion 11⟧
