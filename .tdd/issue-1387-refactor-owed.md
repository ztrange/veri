### For an interface `<name>.sh`, lines in `veri/<name_with_underscores>.py` (the script's own module) are not reported as callers, while a line naming it in any other product file still is ⟦criterion 1⟧
- compute `own` only when `name.endswith(".sh")` (else None) and drop the per-path `.sh` test inside the loop in `main`
- test-only | fold the repeated `new_repo` + `mkdir -p .../veri` + `add`/`commit` fixture setup in no-product-caller.test.sh into one helper
### Files under any `__pycache__/` directory, and any `*.pyc` file, are never scanned: a stale compiled file naming the interface is not reported as a caller ⟦criterion 2⟧
- test-only | extract the repeated per-case fixture setup (`new_repo -b main` + `mkdir -p …/veri` + `printf '# tdd\n' > SKILL.md`) in no-product-caller.test.sh into one helper
applied | f6301239fa9669cd3bb7529aa2608a818dafb6f1 | compute `own` only when `name.endswith(".sh")` (else None) and drop the per-path `.sh` test inside the loop in `main`
