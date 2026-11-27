# Plan for #4814 — refactor: cut the nested-pytest leg cases' real waits and duplicate leg launches

- [x] `idle_watch.py` waits `VERI_PYTEST_TERM_GRACE` seconds (tunable, default `5`) between TERM and KILL ⟦criterion 1⟧
- [x] ⟦skill-edit⟧ skills/tdd/scripts/tests/py/README.md *The idle window* names `VERI_PYTEST_TERM_GRACE`, graded by row CM210<reword> ⟦criterion 1⟧
- [x] every hung-worker case in `test_pytest_leg_idle_process.py` sets `VERI_PYTEST_TERM_GRACE=1`, and no case name says `5_s_later` ⟦criterion 2⟧
- [x] the stacks assertions run on the `workers-end-on-term` launch at `2 * IDLE`; the idle file collects 5 cases ⟦criterion 3⟧
- [x] the three `test_2741_*` cases are one case over one planted tree ⟦criterion 4⟧
- [ ] `test_recipe_one_pytest_process.py` drops the redundant failing-case test and merges the one-pytest case into the 2092 case; 24 cases ⟦criterion 5⟧
