# Plan for #1083 — tick-ledger.sh and clear-refactor-pending.sh exit 1, not 2, when their ledger cannot be read

- [x] tick-ledger.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 1⟧
- [x] tick-ledger.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 2⟧
- [x] clear-refactor-pending.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 3⟧ ⟂ refactor pending
- [ ] clear-refactor-pending.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 3⟧
- [ ] On a readable ledger, tick-ledger.sh and clear-refactor-pending.sh still exit 3 when no step matches and 0 when they tick or clear one ⟦criterion 4⟧
- [ ] No case added or changed on this branch forces an unreadable ledger with permission bits (chmod, a read-only path) or a system location; each uses a directory or a missing path inside its own scratch tree ⟦diff-checked⟧ ⟦criterion 5⟧
