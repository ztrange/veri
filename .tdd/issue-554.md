# Plan for #554 — docs project: copy the walkthrough pipeline into projects/docs/, behaviour-preserving

- [x] projects/docs/ carries the generator and its inputs (build-walkthrough.py, check-walkthrough.py, wt/*, docs-owed.sh, merge-gates.sh, hooks/reference-transaction, walkthrough.html) with ROOT resolved to the repo root two levels up, and `python3 projects/docs/build-walkthrough.py --stdout` is byte-identical to `python3 docs/build-walkthrough.py --stdout` ⟦criterion 2⟧
- [x] the copied docs-owed.sh and merge-gates.sh in projects/docs/ name projects/docs/ paths (walkthrough.html, wt/, tests/) instead of docs/ ones, so each works when run from the copy ⟦added⟧ ⟦criterion 1⟧
- [x] the copied docs-owed.sh in projects/docs/ names projects/docs/ paths (walkthrough.html, wt/, tests/) instead of docs/ ones, so it works when run from the copy ⟦added⟧ ⟦criterion 1⟧
- [ ] a projects/docs/Makefile exists, so the copied scripts and suites that call make from projects/docs/ resolve ⟦added⟧ ⟦criterion 1⟧
- [ ] the seven pipeline suites (build-guards, commentary-figures, docs-guard-filter, docs-owed, generator-inputs, lane-insulation, merge-gates) are copied to projects/docs/tests/ naming projects/docs/… paths, and each ends in its `<n> passed, 0 failed` count line when run directly, with the ADR suites and suite-lanes not copied ⟦criterion 1⟧
- [ ] `make -C projects/docs test` runs every suite globbed from projects/docs/tests/ and fails, naming the suite, one that never reaches its count line ⟦criterion 1⟧
- [ ] projects/docs/Makefile also carries the `docs`, `fresh` and `check` targets, working from the copy's paths
- [ ] projects/docs/CLAUDE.md carries the docs project's working notes (the one trap, the docs command rows, the docs-suite rules) written for the projects/docs/ paths
- [ ] the change touches only paths under projects/docs/, checked by `git diff --stat origin/main...HEAD` ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] the repo-root `make test` and `make docs-test` are green and run exactly the suites they ran before, compared by `make -n` rosters ⟦full-suite⟧ ⟦criterion 4⟧

## Owed steps

- the copied merge-gates.sh in projects/docs/ runs the projects/docs/Makefile targets and tells the user to run the projects/docs/ regen and `git add projects/docs/walkthrough.html`, so it works when run from the copy
