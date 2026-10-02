# Plan for #645 — parallel-conductors.sh restarts each conductor at step-done once its context crosses the budget, and parks halted runs

- [x] with VERI_PARALLEL=2 and two solvable issues, each conductor's assistant events print `context <issue> <tokens>` lines on parallel-conductors.sh's stdout, the figure being cache_read_input_tokens + cache_creation_input_tokens of that event, attributed to the issue whose conductor emitted it ⟦criterion 1⟧
- [x] a parallel-conductors.sh conductor whose context has crossed VERI_CONDUCTOR_CTX_BUDGET is not stopped at the `event.sh step-done` call nor anywhere before it, and is stopped once that call's result appears in its stream ⟦criterion 2⟧
- [x] while one conductor is stopped over VERI_CONDUCTOR_CTX_BUDGET at step-done, the other conductor running beside it is not stopped and runs to its own end ⟦criterion 2⟧
- [x] a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET is launched again by parallel-conductors.sh for the same issue, before any not-yet-launched solvable issue is launched into that slot ⟦criterion 3⟧
- [x] each over-budget restart is recorded where a human can see it: parallel-conductors.sh prints a `restarted <n>` line naming the issue whose conductor it relaunched ⟦criterion 3⟧
- [x] a parallel-conductors.sh conductor that halts after writing `.tdd/parked/<n>.md` makes it print `parked <n>`, its slot then takes the next solvable issue, and issue <n> is not launched again in that invocation even while solvable-issues.sh still lists it ⟦criterion 4⟧
- [ ] a parked conductor does not stop new launches, with or without `--continue-on-bail`: parking is not a bail ⟦criterion 4⟧
- [ ] parallel-conductors.sh exits 2 with a diagnostic naming VERI_CONDUCTOR_CTX_BUDGET, launching no conductor, when it is set to anything that is not a whole number ⟦criterion 5⟧
- [ ] with VERI_PARALLEL=1, a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is stopped only after its step-done result and is relaunched for the same issue, and one that never crosses the budget is never stopped or relaunched ⟦criterion 6⟧
- [ ] with VERI_PARALLEL=1, parallel-conductors.sh exits 0 once nothing is left to take after it launched conductors, and exits 0 when every issue still solvable is parked ⟦criterion 6⟧
- [ ] the new parallel-conductors.sh cases run conductors through a stub `claude` reached by CLAUDE_BIN and an injected clock, with no real model and no real wait ⟦human-owed⟧ ⟦criterion 7⟧
