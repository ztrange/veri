# Plan for #3943 — PRD 017.2: coverage-blocker.sh exits 2 and files nothing when the cover report is missing

- [ ] Every existing coverage-blocker case that runs with no `.tdd/develop-cover.out` writes a `COVERED: no` report first, its assertions unchanged, and passes on unmodified code ⟦criterion 3⟧
- [ ] With `.tdd/develop-cover.out` absent, `coverage-blocker.sh <n>` exits 2, makes no gh call that creates or edits an issue, and names `.tdd/develop-cover.out` on stderr ⟦criterion 1⟧
- [ ] With `.tdd/develop-cover.out` a directory or mode 000, `coverage-blocker.sh <n>` exits 2, makes no gh call that creates or edits an issue, and names `.tdd/develop-cover.out` on stderr ⟦criterion 2⟧
