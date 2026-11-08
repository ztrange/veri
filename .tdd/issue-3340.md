# Plan for #3340 — make test TESTS= runs projects/dashboard/ cases under veri's small-case guard instead of the dashboard's own runner

- [x] `make test TESTS=projects/dashboard/tests/<case>.py` runs that case under the dashboard's own runner (`make -C projects/dashboard test` semantics: `python3 -m pytest` from `projects/dashboard`), not veri's pytest leg and small-case guard, so a dashboard case that starts a real `serve.py` process with no process mark passes and the command exits 0; routing only: no exit propagation, no exit guard (the later Pin step owns exit propagation) ⟦criterion 1⟧
- [x] A `TESTS` list mixing a passing `projects/dashboard/` case and a passing veri case runs the dashboard case under the dashboard's runner and the veri case under veri's pytest leg, and exits 0 ⟦criterion 2⟧
- [x] A `TESTS` list mixing a failing `projects/dashboard/` case and a passing veri case exits non-zero ⟦criterion 2⟧
- [x] A `TESTS` list mixing a passing `projects/dashboard/` case and a failing veri case exits non-zero ⟦criterion 2⟧
- [x] A failing dashboard case run through `make test TESTS=projects/dashboard/...` exits 1 ⟦criterion 3⟧ ⟂ retired unpinnable
- [x] pin: a failing dashboard case makes `make test TESTS=<dashboard path>` exit nonzero; this already holds on the before-state (the small-case guard fails it), so the case passes there and goes red under the mutant that drops `|| fail=1` from the dashboard invocation in the Makefile ⟦added⟧ ⟦criterion 3⟧
- [x] `make test TESTS=projects/dashboard/...` exits 2 when the dashboard's runner cannot start (the dashboard Makefile or its interpreter missing) ⟦criterion 3⟧ ⟂ retired unpinnable
- [x] Veri paths keep veri's rules: under `make test TESTS=<veri path>`, an unmarked veri case that spawns `git` or `python3` still refuses ⟦criterion 4⟧ ⟂ retired unpinnable
- [ ] Go-red: with the dashboard delegation removed, the first criterion's case goes red ⟦human-owed⟧ ⟦criterion 5⟧
