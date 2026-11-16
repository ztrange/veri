# Plan for #4049 — PRD 025.12: orchestrate.sh is gone

- [ ] parallel_conductors.main refuses a bad VERI_CONDUCTOR_CTX_BUDGET with exit 2 before it runs any git command, and the #1313 tunables case names veri.parallel_conductors for it ⟦criterion 5⟧
- [ ] orchestrate.sh, veri/orchestrate.py, test_orchestrate_process.py and unit/test_orchestrate.py are deleted, and veri/README.md and every test listing name orchestrate no more ⟦criterion 1⟧ ⟦criterion 3⟧
- [ ] VERI_CONDUCTOR_STOP_TIMEOUT, stop_timeout and STOP_TIMEOUT_MAX leave tunables.py, VERI_CONDUCTOR_CTX_BUDGET stays, and context_budget.py's docstring names only parallel_conductors.py ⟦criterion 2⟧
- [ ] parallel-conductors.sh's exit codes and output are unchanged: test_parallel_conductors.py passes with only the refused-budget row's exclude changed ⟦criterion 4⟧
