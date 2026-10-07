# Plan for #1118 — tick-ledger.sh and clear-refactor-pending.sh exit 2, not 1 with a traceback, on every ledger read failure

- [x] tick-ledger.sh exits 2 with one `tick-ledger.sh: <path>: <reason>` stderr line and no traceback, writing nothing, when reading the ledger fails with an OSError other than a missing file or a directory — a ledger path running through a regular file ⟦criterion 1⟧
- [x] tick-ledger.sh exits 2 with one `tick-ledger.sh: <path>: <reason>` stderr line and no traceback, leaving the ledger byte-identical, when the ledger holds bytes that do not decode under a UTF-8 locale ⟦criterion 1⟧ ⟂ refactor pending
- [ ] clear-refactor-pending.sh exits 2 with one `clear-refactor-pending.sh: <path>: <reason>` stderr line and no traceback, writing nothing, when reading the ledger fails with an OSError other than a missing file or a directory — a ledger path running through a regular file ⟦criterion 1⟧
- [ ] no case this branch adds forces a ledger read failure with permission bits or a system path: each forces it by the path's type or shape inside its scratch tree (a path through a regular file, a symlink loop, undecodable bytes), or by faking the read at the process boundary in tests/py/ ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] the Exit lines of tick-ledger.sh and clear-refactor-pending.sh name a ledger that could not be read under exit 2, not exit 1 ⟦diff-checked⟧
