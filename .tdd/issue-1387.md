# Plan for #1387 — no-product-caller.sh reports a script's own Python module and stale __pycache__ files as callers

- [x] For an interface `<name>.sh`, lines in `veri/<name_with_underscores>.py` (the script's own module) are not reported as callers, while a line naming it in any other product file still is ⟦criterion 1⟧
- [x] Files under any `__pycache__/` directory, and any `*.pyc` file, are never scanned: a stale compiled file naming the interface is not reported as a caller ⟦criterion 2⟧
- [x] Each exclusion is watched red by hand: with the module exclusion removed the module's own lines are reported again, and with the `__pycache__`/`*.pyc` exclusion removed a planted stale `.pyc` is reported again ⟦human-owed⟧ ⟦criterion 3⟧
