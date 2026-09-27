# Plan for #452 — A crossing, a cost-driven split and a cost-driven park are distinct marks in the run's event log

- [x] SKILL.md's step cost check writes one `step-over-budget` event carrying `spent=` and `budget=` at the crossing, before the over-budget leaf is launched ⟦criterion 1⟧
- [x] SKILL.md writes that `step-over-budget` event on every crossing, so a crossing that goes on to split, one that goes on to park and one that goes on to continue each carry it ⟦criterion 2⟧
- [ ] SKILL.md's over-budget exit 0 branch writes `step-split` carrying `at=over-budget`, while the revise-exhausted split keeps its `at=exhausted` spelling unchanged ⟦criterion 3⟧
- [ ] SKILL.md's over-budget exit 1 branch writes `step-escalated` carrying `at=over-budget` ⟦criterion 4⟧
- [ ] SKILL.md's over-budget exit 3 branch writes no event mark beyond the crossing's `step-over-budget` ⟦criterion 5⟧
- [ ] metrics.sh's `#### By step` table reports, for a step whose log holds `step-over-budget`, the `spent=` figure it carried, and leaves that column empty for a step that did not cross ⟦criterion 6⟧
- [ ] metrics.sh's report distinguishes a log holding `step-split` with `at=over-budget` from one holding `step-split` with `at=exhausted` ⟦criterion 7⟧
- [ ] classify-bail.sh refuses `step-over-budget` and `over-budget` as bail causes, knowing none of the new words ⟦criterion 8⟧
