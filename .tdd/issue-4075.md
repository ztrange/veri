# Plan for #4075 — PRD 013.9: plan growth is bounded relative to the verified plan

- [x] `VERI_STEP_GROWTH_PERCENT` is a `TUNABLES` entry, default 50, parsed by `tokens` ⟦criterion 3⟧
- [x] `ledger-growth.sh` caps ⟦added⟧ steps at ⌈percent × P ÷ 100⌉, P the plan ledger's steps, and exits 2 on a refused percent ⟦criterion 2⟧
- [x] `add-ledger-step.sh` caps the batch at ⌈percent × P ÷ 100⌉, P the steps at the plan-sha commit, and exits 2 on a refused percent ⟦criterion 1⟧
- [x] a set `VERI_STEP_GROWTH` makes both scripts exit 2 naming `VERI_STEP_GROWTH_PERCENT` ⟦criterion 4⟧
- [x] preflight stops at step 5 on a set `VERI_STEP_GROWTH` or a refused `VERI_STEP_GROWTH_PERCENT` ⟦criterion 5⟧
- [ ] a tree_audit case refuses `VERI_STEP_GROWTH` outside the retired-naming files ⟦criterion 10⟧
- [x] ADR-0022, veri/README.md and both script headers name `VERI_STEP_GROWTH_PERCENT` ⟦criterion 9⟧
- [x] ⟦skill-edit⟧ `skills/tdd/SKILL.md` says "the growth cap", no larger in bytes ⟦criterion 6⟧
- [x] ⟦skill-edit⟧ `CLAUDE.md` names `VERI_STEP_GROWTH_PERCENT` as the plan-growth budget ⟦criterion 7⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/BAIL.md` and the other skill docs and `CONTEXT.md` name `VERI_STEP_GROWTH_PERCENT` ⟦criterion 8⟧
