# Plan for #4391 — PRD 038.12: bail.sh bails a run (BAIL.md 1-8) in one call, never refusing

- [ ] `bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]` runs BAIL.md 1–7 in order: preserve-attempt, reset, classify and the `bail` event, metrics and its commit, push, the bailed comment on the issue (note + metrics block + skill-drift block) and on the PR (BLS1) ⟦criterion 1⟧
- [ ] a failing preserve-attempt, metrics render, push, skill-drift read or comment is named on its call line, every later call still runs, exit 0 with the `bail` event written (BLS2) ⟦criterion 2⟧
- [ ] an unknown cause or bad arguments exit 2 before any reset or event, the last line naming BAIL.md sub-step 1, the tree untouched (BLS3) ⟦criterion 3⟧
- [ ] the cause is taken as given: a `needs-user` bail's event carries it (BLS4) ⟦criterion 4⟧
- [ ] its last lines are the phase, classification, branch and worktree; one line per call with its exit code, never a call's output (BLS5) ⟦criterion 5⟧
- [ ] BAIL.md names the call before sub-step 1 (BL178) and SCRIPTS.md lists the script (SC588), both graded; no other `Read BAIL.md` site and SKILL.md unchanged (BLS6) ⟦criterion 6⟧
