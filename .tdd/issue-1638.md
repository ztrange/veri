# Plan for #1638 — A failed re-apply's stop message names only some of the saved .tdd/ appends files

- [x] When rebase_onto_default.py cannot re-apply a set-aside-tdd-appends.diff a killed run left, its exit-2 stop names that set-aside file and every kept-tdd-appends.diff* file on disk, pinned by a case with both kinds of file present ⟦criterion 1⟧ ⟂ refactor pending
- [ ] When rebase_onto_default.py cannot re-apply the uncommitted .tdd/ appends after its rebase, its exit-2 stop names the set-aside-tdd-appends.diff it left on disk as well as every kept-tdd-appends.diff* file, pinned by a case with both kinds of file present ⟦criterion 1⟧
- [ ] When SKILL.md's resume discard cannot re-apply the uncommitted .tdd/ appends, its exit-2 stop names a set-aside-tdd-appends.diff already on disk as well as every kept-tdd-appends.diff* file, pinned by a case running the discard as SKILL.md writes it with both kinds of file present ⟦criterion 1⟧
