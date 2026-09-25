# Plan for #449 — `step-budget.sh`: VERI_STEP_BUDGET and VERI_RUN_BUDGET resolved, validated, and refused in preflight

- [x] step-budget.sh with neither VERI_STEP_BUDGET nor VERI_RUN_BUDGET set prints 12 then 120, each on its own line, and exits 0 ⟦criterion 1⟧
- [x] step-budget.sh prints a set VERI_STEP_BUDGET then a set VERI_RUN_BUDGET, decimal values included, in that order ⟦criterion 2⟧
- [x] A VERI_STEP_BUDGET that is not a non-negative decimal number exits 2, names VERI_STEP_BUDGET on stderr, and prints nothing on stdout ⟦criterion 3⟧
- [x] A VERI_RUN_BUDGET that is not a non-negative decimal number exits 2, names VERI_RUN_BUDGET on stderr, and prints nothing on stdout ⟦criterion 4⟧
- [x] Both budget variables invalid at once exits 2 and prints nothing on stdout, not the first figure then a failure ⟦criterion 5⟧
- [ ] Either budget variable exported as the empty string exits 2 rather than falling back to its default ⟦criterion 6⟧
- [ ] A budget of 0 is accepted for either variable and printed back ⟦criterion 7⟧
- [ ] step-budget.sh given any argument exits 2 ⟦criterion 8⟧
- [ ] The step-budget suite lives in skills/tdd/scripts/tests/unit/ and its header states the fast-tier bar: no git, no network, no servers, no real sleep, no nested suites ⟦criterion 9⟧
