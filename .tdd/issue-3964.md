# Plan for #3964 — PRD 022.7: a run stops when its skill snapshot was changed

- [ ] `pinned_scripts.snapshot_digest` lists every file of a snapshot, path and content, the `.veri-snapshot` marker excluded: it changes when one file's content changes and not when only the marker does ⟦criterion 1⟧
- [ ] after `extract` and `write_snapshot_marker`, `run_conductor.main` writes the snapshot's digest to `.tdd/issue-<n>-snapshot-digest` in the main working tree ⟦criterion 1⟧
- [ ] `supervise.sh` refuses to launch a leaf of run `<n>` from a snapshot one of whose files was edited since its digest: `supervise: refusing to launch <name>: the skill snapshot <path> changed since extraction`, exit 2, no leaf ⟦criterion 2⟧
- [ ] a launch with `VERI_SKILL_UNPINNED=1`, or with no `.tdd/issue-<n>-snapshot-digest`, skips the snapshot check ⟦criterion 3⟧
- [ ] at the conductor's exit `run_conductor.main` recomputes the digest before removing the snapshot; on a mismatch it prints `run-conductor: the skill snapshot changed during the run`, appends a `snapshot-changed` event and exits 2; `JOURNAL.md` lists the event ⟦criterion 4⟧ ⟦criterion 5⟧
- [ ] README.md's *The skill snapshot* paragraph says the snapshot is digest-checked before each leaf launch and at exit, what a mismatch does, and the limit (RD30) ⟦criterion 6⟧
