# Plan for #4092 — PRD 016.7: run preflight refuses on a failing readiness row

- [x] `ready-check.sh --no-suites` is accepted, prints no `<tier> tier run` row and runs no test tier ⟦criterion 5⟧
- [x] preflight runs `ready-check.sh --no-suites` after step 2's checks pass and before step 3 creates the worktree ⟦criterion 1⟧
- [x] a failing step 2 check stops preflight before `ready-check.sh` runs ⟦criterion 1⟧
- [x] a failing refusing row stops preflight at `2 ready-check.sh` with exit 1, its fail line printed and no worktree created ⟦criterion 2⟧
- [ ] any other failing row is printed and preflight goes on ⟦criterion 3⟧
- [ ] an exit 2 from `ready-check.sh` stops preflight at `2 ready-check.sh` with exit 2 ⟦criterion 4⟧
- [ ] a stop at `2 ready-check.sh` writes no event and posts no comment ⟦criterion 6⟧
- [ ] PREFLIGHT.md step 2 says preflight runs `ready-check.sh --no-suites` and which failing rows stop the run ⟦criterion 7⟧
- [ ] PREFLIGHT-FAILURES.md `### Step 2` says a stop at `2 ready-check.sh` is a refusal recorded by `preflight-refused.sh` ⟦criterion 8⟧
