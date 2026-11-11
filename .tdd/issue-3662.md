# Plan for #3662 — A tree_audit case gets the longer per-case timeout a process case gets, so a whole-tree audit cannot bail a run under load

- [x] A `tree_audit` case with no `timeout` mark of its own runs under the timeout a `process` case gets, `max(PROCESS_CASE_TIMEOUT, --timeout)`, where today it keeps the session's `--timeout`; the Red case sits in skills/tdd/scripts/tests/py/test_conftest.py beside the existing process-case timeout case, and fails on the current conftest ⟦guard-subject: skills/tdd/scripts/tests/py/conftest.py⟧ ⟦criterion 1⟧
- [ ] A `tree_audit` case carrying an explicit `timeout` mark of its own keeps that mark's timeout, not the `process`-case default ⟦criterion 1⟧
- [ ] `CLAUDE.md`'s Testing idiom, where it names the 90 s `process` case default (`PROCESS_CASE_TIMEOUT`), names the `tree_audit` case alongside it, with the root `REQUIREMENTS.md` row CM53 amended to match ⟦skill-edit⟧ ⟦criterion 2⟧
