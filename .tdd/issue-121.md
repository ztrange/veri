# Plan for #121 — Size the leaf timeout from the baseline run: VERI_TIMEOUT defaults to a multiple of the measured suite time

- [x] `leaf-timeout.sh <baseline-seconds>` prints the hard timeout for the run when `VERI_TIMEOUT` is unset: the larger of 900 and 6 × the baseline's wall time, as a whole number of seconds; a baseline that is not a whole number ≥ 0 is exit 2 with a diagnostic on stderr and nothing on stdout
- [x] an explicit `VERI_TIMEOUT` is printed as given, whatever the baseline measured; a `VERI_TIMEOUT` that is not a whole number ≥ 1 is exit 2, fail closed, the way `refactor-budget.sh` treats its budget
- [x] SKILL.md's preflight times the baseline run, derives the timeout with the script, hands it to every leaf launch as `VERI_TIMEOUT`, and the plan comment states the timeout and how it was chosen — pinned as text, the way `skill-identity.test.sh` pins SKILL.md
