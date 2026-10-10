# Plan for #1448 — build-develop-prompt.sh revise refuses the interface phases (expand, migrate, contract-a, contract-b), so a phased step's REJECT bails instead of revising

- [x] `build-develop-prompt.sh revise <phase> <spec> "<step>" '<test-cmd>' <reason-file> '<fast-cmd>'` exits 0 for each of expand, migrate, contract-a and contract-b, printing a revise prompt that names the phase being redone and carries the rejection reason verbatim, where it exited 2 with "unknown phase to revise"
- [ ] The revise prompt for an interface phase states that phase's freeze rule, so the redone work passes the freeze check the conductor runs on it: test files are never modified when redoing expand, migrate or contract-b, and production files are never modified when redoing contract-a
