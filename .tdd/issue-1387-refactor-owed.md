### For an interface `<name>.sh`, lines in `veri/<name_with_underscores>.py` (the script's own module) are not reported as callers, while a line naming it in any other product file still is ⟦criterion 1⟧
- compute `own` only when `name.endswith(".sh")` (else None) and drop the per-path `.sh` test inside the loop in `main`
- test-only | fold the repeated `new_repo` + `mkdir -p .../veri` + `add`/`commit` fixture setup in no-product-caller.test.sh into one helper
