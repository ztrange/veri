# Plan for #4534 — test-quality.sh record drops the whole report when one finding names a non-test helper

- [x] `test-quality.sh record` given one valid finding and one naming a non-test helper exits 0, writes the valid finding and names the refused one on stderr ⟦criterion 1⟧
- [ ] `test-quality.sh record` given a report whose every finding is refused exits 2 and writes nothing ⟦criterion 2⟧
- [ ] the per-finding skip, broken on purpose (exit 2 on the first refusal), turns the criterion 1 case red ⟦criterion 3⟧
- [ ] the shim header, the `SCRIPTS.md` catalogue entry, `DRAFT-PR.md` sub-step 1 and row SC398 state the per-finding skip, regraded
