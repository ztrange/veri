# Plan for #451 — SKILL.md's pre-green-commit cost checkpoints, and the three-way branch on a crossing

- [x] SKILL.md's preflight calls `step-budget.sh` beside `refactor-budget.sh 0`, and its exit 2 is a preflight-class stop before any leaf is launched ⟦criterion 1⟧
- [x] SKILL.md places a `step-cost.sh` cost check against the step budget after develop-red, after each verify-red, after each revise attempt, after develop-green and after each verify-green ⟦criterion 2⟧
- [x] SKILL.md says in prose, not only in an inline comment, that the shared revise block runs `step-cost.sh` only when the phase being revised is red or green, never for a refactor-phase revise ⟦added⟧ ⟦criterion 2⟧
- [x] SKILL.md places no cost check after the step's green commit — not in the refactor loop, not after verify-refactor — and says why ⟦criterion 2⟧
- [x] SKILL.md runs each cost check only once the leaf has exited and its `usage` event has been harvested
- [x] SKILL.md states that the cost check fires at most once per step and is not re-armed once its branch has run ⟦criterion 3⟧
- [x] SKILL.md states that `step-cost.sh` exit 3 (no leaf of this step has reported yet) is not a crossing ⟦criterion 4⟧
- [x] SKILL.md's crossing branch builds the `over-budget` prompt, launches its leaf through `supervise.sh` the way the exhausted leaf is launched, and reads its answer with `exhausted-outcome.sh`, never by eye ⟦criterion 5⟧
- [x] The over-budget exit 0 branch restores the tree (`git reset --hard HEAD`, `git clean -f -- <test-path>`) before growing the plan, grows it in one `add-ledger-step.sh instead-of` call, and commits the plan before the run continues ⟦criterion 6⟧
- [x] The over-budget exit 0 branch treats `add-ledger-step.sh` exit 1 as a `step-too-big` bail ⟦criterion 7⟧ ⟂ refactor pending
- [ ] The over-budget exit 1 branch parks the step carrying the leaf's answer and the spent and budget figures, and leaves the plan unchanged ⟦criterion 8⟧
- [ ] The over-budget exit 3 branch records the crossing and continues the step, and SKILL.md says in so many words that it is not a bail and why ⟦criterion 9⟧
- [ ] SKILL.md states once, in the over-budget section, why a crossing is not a failure and why no exit code changes meaning
- [ ] A supervisor exit 2 on the over-budget leaf is a `killed-stuck` bail, and SKILL.md says the step's budget stays crossed rather than re-arming ⟦criterion 10⟧
- [ ] `make unit` and every SKILL.md prose suite (`skill-*.test.sh`) pass against the finished SKILL.md ⟦criterion 11⟧
