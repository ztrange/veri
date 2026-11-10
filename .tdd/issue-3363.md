# Plan for #3363 — pin-recheck takes only a base sha, so a re-record-only step replays all 144 records and hits the 900 s timeout

- [ ] Without the --ledger flag, pin-recheck.sh <base> replays every touched record of every .tdd/issue-*-mutations.md ledger, as today: the replay set is unchanged ⟦criterion 3⟧
- [ ] pin-recheck.sh <base> --ledger <file> replays only the records of that one mutations ledger that the range touches; a record of another ledger whose file the range also touches is not replayed ⟦criterion 1⟧
- [ ] pin-recheck.sh <base> --ledger <file> whose ledger holds no record the range touches exits 3 and replays nothing, never widening to all records ⟦criterion 2⟧
- [ ] `skills/tdd/SCRIPTS.md`'s pin-recheck.sh entry is reworded to state the optional --ledger <file> selector in its synopsis: it replays only that ledger's records the range touches, a selector matching no record exits 3, and without it the replay set is unchanged ⟦skill-edit⟧ ⟦criterion 4⟧
- [ ] pin-recheck.sh's usage line states the --ledger <file> selector: run with no argument it still exits 2 and its usage line names the optional --ledger <file>, and the shim's Usage header names it too; this step's Red updates the existing no-argument case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py to the new usage line, so no older case pins the old text when Green changes it ⟦criterion 4⟧
