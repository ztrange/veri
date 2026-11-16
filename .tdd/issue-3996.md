# Plan for #3996 — PRD 021.12: `conductor.pid` has one writer

- [x] a claim whose `ps` gives no start time writes `<pid>\n` to `conductor.pid`, not `<pid>\n\n`; a small case in `tests/py/unit/test_run_conductor.py` ⟦criterion 3⟧
- [x] the claim in `run_conductor.main` and `record_pid` both write `conductor.pid` through `pid_file.record`, which returns the text it wrote; the existing `conductor.pid` cases pass unchanged ⟦criterion 1⟧
- [x] `git grep -n 'lstart' -- skills/tdd/scripts/veri/run_conductor.py` finds no line composing a pid file's text ⟦criterion 2⟧
