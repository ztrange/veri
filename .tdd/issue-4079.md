# Plan for #4079 — PRD 013.18: a run's local records reach any machine

- [x] `push-branch.sh` also pushes `refs/veri/runs/<n>`, a commit on no branch holding the run's `.tdd/events.jsonl` lines for issue `<n>`, `.tdd/issue-<n>-skill-commit` and `.tdd/issue-<n>-timeout` ⟦criterion 1⟧
- [x] `queued-merge.sh` deletes `refs/veri/runs/<n>` on origin once the PR reads MERGED, and leaves it when the PR does not ⟦criterion 2⟧
- [x] `metrics.sh <n>`, with no events for issue `<n>` in the local `.tdd/events.jsonl`, reports from the events in origin's `refs/veri/runs/<n>` ⟦criterion 3⟧
- [x] `run-conductor.sh <n>`, with no local `.tdd/issue-<n>-skill-commit`, pins the run to the commit origin's `refs/veri/runs/<n>` records ⟦criterion 4⟧
