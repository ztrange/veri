# Plan for #4079 — PRD 013.18: a run's local records reach any machine

- [x] `push-branch.sh` also pushes `refs/veri/runs/<n>`, a commit on no branch holding the run's `.tdd/events.jsonl` lines for issue `<n>`, `.tdd/issue-<n>-skill-commit` and `.tdd/issue-<n>-timeout` ⟦criterion 1⟧
- [x] `queued-merge.sh` deletes `refs/veri/runs/<n>` on origin once the PR reads MERGED, and leaves it when the PR does not ⟦criterion 2⟧
- [x] `metrics.sh <n>`, with no events for issue `<n>` in the local `.tdd/events.jsonl`, reports from the events in origin's `refs/veri/runs/<n>` ⟦criterion 3⟧
- [x] `run-conductor.sh <n>`, with no local `.tdd/issue-<n>-skill-commit`, pins the run to the commit origin's `refs/veri/runs/<n>` records ⟦criterion 4⟧
- [ ] the records push and fetch end after `VERI_GIT_NETWORK_TIMEOUT` seconds: a timeout is one stderr line and no answer, never a hang ⟦criterion 1⟧
- [ ] any exception from the pointer update or the records push leaves `push-branch.sh`'s exit code unchanged ⟦criterion 1⟧
- [ ] the carried journal keeps lines naming no issue, as the report counts them ⟦criterion 1⟧
- [ ] the ref carries only what a reader restores: the issue's journal lines and the skill pin, not the timeout pin ⟦criterion 1⟧
- [ ] `run-conductor.sh` honours a carried skill pin only when it is an ancestor of the skill clone's origin default branch, else names it on stderr and pins fresh ⟦criterion 4⟧
- [ ] `release-issue.sh` deletes origin's `refs/veri/runs/<n>` once the run is released; a failure is one stderr line, never fatal ⟦criterion 2⟧
