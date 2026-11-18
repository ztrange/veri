# Plan for #4295 — check-earlier accepts a file that is not the run's ledger and exits 0 with a pass marker

- [x] With `VERI_ISSUE=<n>`, `check-earlier .tdd/plan-ledger.md --step <s>` exits 2, its stderr names the ledger and `.tdd/issue-<n>.md`, and no `check-earlier-*.pass` marker is left ⟦criterion 1⟧
- [ ] On a `tdd/<n>-` branch with `VERI_ISSUE` unset, `check-earlier` on a ledger that is not `.tdd/issue-<n>.md` exits 2 the same way
- [ ] With `VERI_ISSUE=<n>`, `check-earlier` given the run's own `.tdd/issue-<n>.md` by its absolute path exits 0 and writes its pass marker ⟦criterion 2⟧
- [ ] The `Exit:` comment of `tests-frozen.sh` and the `SCRIPTS.md` catalogue entry name the new exit 2 ⟦criterion 3⟧
