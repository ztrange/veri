# Plan for #3966 — PRD 022.19: make test refuses a bytecode cache it does not own

- [x] `make test` and `make unit` create an absent prefix with mode `0700` and run ⟦criterion 1⟧
- [x] with the prefix group-writable, both refuse with one line naming the path and the fix and exit 2 before any suite ⟦criterion 2⟧
- [x] the same with the prefix other-writable ⟦criterion 2⟧
- [x] the same with the prefix a symlink to a closed directory of the user's own ⟦criterion 2⟧
- [ ] the same with the prefix a closed directory owned by another user ⟦criterion 2⟧
- [ ] CLAUDE.md's bytecode-cache paragraph names the refusal (CM161), graded ⟦criterion 3⟧
