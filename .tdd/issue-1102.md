# Plan for #1102 — run-leaf: every plumbing failure in run_leaf.py exits 2, not 1

- [x] a prompt file that cannot be read (a directory given as the prompt file, inside the case's scratch tree) makes run_leaf.main return 2, not 1, launch no leaf, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧
- [x] copying ~/.gitconfig into the leaf's temp git config raising OSError (faked at the process boundary in tests/py/) makes run_leaf.main return 2, not 1, launch no leaf, leave no temp file, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧
- [x] the stream temp file in $TMPDIR vanishing during the leaf's run, so the re-read after the leaf ends fails, makes run_leaf.main return 2, not 1, and still print its one `run-leaf.sh: <path>: <reason>` stderr line ⟦criterion 1⟧ ⟂ refactor pending
- [ ] each of the three failure paths has a case that forces it using the path's type or shape inside the case's scratch tree, or a fake at the process boundary in tests/py/, and no case on this branch forces a failure with permission bits or a system path ⟦diff-checked⟧ ⟦criterion 2⟧
