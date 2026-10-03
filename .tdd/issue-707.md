# Plan for #707 — dashboard_endpoints.py and veri/status.py build a run's .tdd/ path through one run_file(run, name)

- [x] A function `run_file(run, name)` in a module of `skills/tdd/scripts/veri/` returns the path of `<name>` inside the run directory's `.tdd/` directory (`<run>/.tdd/<name>`), for a plain name and for a glob pattern alike ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `veri/status.py` builds its per-run `.tdd/` paths (`events.jsonl`, `conductor.pid`, `issue-<n>.md`) through `run_file`, with no `os.path.join(run, ".tdd"` left in it; the `.tdd/wt/*` registry glob is untouched ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] `dashboard_endpoints.py` builds its six per-run `.tdd/` paths (`events.jsonl`, `issue-<n>.md`, `issue-<n>-spec.md`, the leaf's supervised log, the leaf's conductor out, the `*` conductor-out glob) through `run_file`, with no `os.path.join(run, ".tdd"` left in it; the `.tdd/wt/*` registry glob is untouched ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] Both scripts' outputs and exit codes are unchanged: the branch's diff modifies none of `dashboard.test.sh`, `status.test.sh` or `tests/py/test_status.py`, and all three pass ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧
