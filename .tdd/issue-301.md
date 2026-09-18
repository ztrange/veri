# Plan for #301 — hermetic-suites.test.sh re-runs 20 suites under an offline shim, so make test runs a third of itself twice

- [x] `make test` runs every suite under the offline shim with a per-suite reach log, so a suite that runs `git fetch` against a remote URL, `gh` or `curl` fails `make test`, naming the suite and what it tried ⟦criterion 3⟧
- [x] A suite that fetches this checkout's own origin still fails `make test`, named — the own-origin guarantee holds from the recipe's single run, not from a re-run ⟦criterion 5⟧
- [x] No suite is run more than once by a single `make test` for the offline check: hermetic-suites.test.sh re-runs no suite for the offline or own-origin cases ⟦criterion 2⟧
- [x] The ambient-`VERI_*` and conductor-lock cases still hold: a suite whose result changes with an ambient `VERI_*` value or a live conductor lock still fails, named ⟦criterion 4⟧
- [x] hermetic-suites.test.sh runs solvable-issues.test.sh's reference (no-lock, cleared) arm once, shared by its ambient and lock cases, instead of once per case ⟦criterion 1⟧ ⟂ refactor pending
