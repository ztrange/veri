# Plan for #3963 — PRD 022.17: the skill snapshot is read-only

- [ ] `pinned_scripts.make_read_only` removes the write bits of every file and directory of a tree: a write into one of its files fails with a permission error ⟦criterion 1⟧
- [ ] making a tree read-only never follows a symlink out of it: a file a symlink in the tree names keeps its write bits
- [ ] the conductor's removal of the snapshot at exit restores write permission first and leaves no file of a read-only snapshot behind ⟦criterion 2⟧
- [ ] `issue-worktree.sh --remove` restores write permission first and leaves no file of a read-only snapshot `snapshot_made_for` accepts behind ⟦criterion 3⟧
- [ ] `keep_pinned_scripts` replaces a read-only `.tdd/pinned-scripts` on the next of two launches ⟦criterion 4⟧
- [ ] after `extract` and `write_snapshot_marker`, `run_conductor.main` makes the snapshot read-only: a write into a file of a fresh snapshot fails with a permission error ⟦criterion 1⟧
- [ ] README.md's *The skill snapshot* paragraph says the snapshot is read-only (RD29) ⟦criterion 5⟧
