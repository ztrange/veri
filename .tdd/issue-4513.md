# Plan for #4513 — #4450's mutation records on skill_edit_half.py are stale on main: 5 of 11 record old text the file no longer holds

- [x] the 5 records in `.tdd/issue-4450-mutations.md` whose old text `skills/tdd/scripts/veri/skill_edit_half.py` no longer holds are retired, with the reason ⟦criterion 1⟧
- [x] `run-finished.sh <n>` exits 1 with a `stale-pin` line for each unretired record of the run's own mutation record whose old text its mutated file in the run's worktree no longer holds ⟦criterion 2⟧
- [x] a `before` entry and an entry whose mutated file is gone add no `stale-pin` line to `run-finished.sh`, and its stderr hint names the record ⟦added⟧ ⟦criterion 2⟧
- [x] `queued-merge.sh` exits 1 unmerged, the lock released, naming each stale pin of the PR's issue's mutation record ⟦added⟧ ⟦criterion 2⟧
- [x] a join of a run, online and offline, exits 1 before any rebase or push when the run's mutation record holds a stale pin ⟦added⟧ ⟦criterion 2⟧
- [x] `/vmerge` step 4 runs `run-finished.sh <n>` before the merge call and stops, the lock released, on its exit 1 or 2; SCRIPTS.md gains a `run-finished.sh` entry ⟦added⟧ ⟦criterion 2⟧
