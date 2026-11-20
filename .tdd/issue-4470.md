# Plan for #4470 — vmerge says never merge on an empty check rollup, but queued_merge merges on it

- [x] `skills/vmerge/SKILL.md` step 3 rewords "An empty or missing rollup is not a pass" to say when an empty rollup is merged on (`VERI_CI_ON_PR=0` after the local full-suite re-run; unset with no `pull_request` workflow) and when it is waited on (`VERI_CI_ON_PR=1`; unset with such a workflow), matching `wait-ci.sh` and `queued-merge.sh`, graded by its reworded M6 row ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] `skills/tdd/DRAFT-PR.md`'s fail-closed CI sentence rewords "an empty rollup is never a pass" to carry the same `VERI_CI_ON_PR` exception for an empty rollup, graded by its reworded DP45 row ⟦skill-edit⟧ ⟦criterion 2⟧
