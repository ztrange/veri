# Plan for #42 — Refactor loop has a deterministic budget: VERI_REFACTOR_BUDGET transforms per step

- [x] with the default budget, refactor-budget.sh exits 0 for count 0 and 1 and exits 3 for count 2, printing a one-line status
- [x] VERI_REFACTOR_BUDGET=0 makes count 0 exit 3, so a run may switch the refactor loop off entirely
- [ ] a non-numeric or negative VERI_REFACTOR_BUDGET exits 2 with a diagnostic on stderr and no status on stdout
