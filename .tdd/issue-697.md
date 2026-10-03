# Plan for #697 — add-ledger-step.sh refuses an unknown position word instead of exiting 0 with nothing inserted

- [x] add-ledger-step.sh given a position word other than after, before or instead-of exits 2 and its stderr names that word ⟦criterion 1⟧
- [x] after an unknown-position-word call the ledger is byte-identical and gains no ## Owed steps bullet, even when the batch would exceed VERI_STEP_GROWTH ⟦criterion 2⟧
- [x] the branch leaves every existing case in add-ledger-step.test.sh unmodified, so after, before and instead-of keep today's behaviour ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 4⟧
