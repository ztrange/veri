# Plan for #3963 — PRD 022.17: the skill snapshot is read-only

- [ ] the conductor's removal of the snapshot at exit restores write permission first and leaves no file of a read-only snapshot behind ⟦criterion 2⟧
- [ ] `issue-worktree.sh --remove` restores write permission first and leaves no file of a read-only snapshot `snapshot_made_for` accepts behind ⟦criterion 3⟧
- [ ] `keep_pinned_scripts` replaces a read-only `.tdd/pinned-scripts` on the next of two launches ⟦criterion 4⟧
- [ ] after `extract` and `write_snapshot_marker`, `run_conductor.main` removes the write bits of every file and directory of the snapshot: a write into a file of a fresh snapshot fails with a permission error ⟦criterion 1⟧
- [ ] making the snapshot read-only never follows a symlink out of it: a file a snapshot symlink names keeps its write bits
- [ ] README.md's *The skill snapshot* paragraph says the snapshot is read-only (RD29) ⟦criterion 5⟧
