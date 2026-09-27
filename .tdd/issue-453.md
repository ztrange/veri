# Plan for #453 — `run-affordable.sh`: a run parks when it can no longer afford to finish, not when it crosses the ceiling

- [x] `run-affordable.sh <n>`, run from a worktree whose event log holds completed full steps, exits 1 and prints spent, steps remaining, the median full-step cost and the projection when `spent + n × median` exceeds `VERI_RUN_BUDGET` ⟦criterion 1⟧
- [x] `run-affordable.sh <n>` exits 0 and prints nothing when `spent + n × median` is within `VERI_RUN_BUDGET` ⟦criterion 2⟧
- [x] The median is taken over completed full steps only, told apart by leaf count from `step-cost.sh --steps`, so a log whose completed steps are mostly cheap pins still projects the remainder at the full-step median ⟦criterion 3⟧
- [x] `run-affordable.sh <n>` exits 3 with nothing on stdout when the event log holds no completed full step, only pins or no usage at all ⟦criterion 4⟧
- [ ] `run-affordable.sh` exits 2 with nothing on stdout for a missing or non-whole-number `<steps-remaining>` argument ⟦criterion 5⟧
- [ ] `run-affordable.sh <n>` exits 2 with nothing on stdout when `.tdd/events.jsonl` is missing ⟦criterion 5⟧
- [ ] `run-affordable.sh <n>` exits 2 with nothing on stdout when `VERI_RUN_BUDGET` is not a non-negative decimal number ⟦criterion 5⟧
- [ ] A run at 8 of 9 steps done with one median step left and a ceiling above the projection is exit 0, so a converging run near its finish is not parked ⟦criterion 6⟧
- [ ] A run early in a long plan whose projection exceeds the ceiling is exit 1, so it parks while parking is still cheap ⟦criterion 7⟧
- [ ] `SKILL.md` calls `run-affordable.sh` at each step boundary, after a step's ledger commit, with the remaining count `next-unchecked.sh` implies, and parks on exit 1 with a comment carrying spent, steps remaining, the median, the projection, the ceiling and the two answers (raise `VERI_RUN_BUDGET` and resume, or split the issue) ⟦criterion 8⟧
- [ ] `SKILL.md` states that an affordability park is not a bail and that `classify-bail.sh` is not called on it ⟦criterion 9⟧
