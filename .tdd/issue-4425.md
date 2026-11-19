# Plan for #4425 — affected-suites.sh lists a ported module's process test file in the changed tier

- [x] a `veri/<m>.py` change lists `tests/py/test_<m>_process.py` when it exists, besides `test_<m>.py` and `unit/test_<m>.py` ⟦criterion 1⟧
- [ ] a `<name>.sh` shim change lists `tests/py/test_<name with underscores>_process.py` when it exists ⟦criterion 2⟧
- [ ] a ported module or shim change lists every `tests/py/test_*_process.py` that imports or runs it by name (`veri.<m>`, `<m>.py`, `<m>.sh`), and a process file naming neither lists nothing ⟦criterion 3⟧
- [ ] a module no process file names lists the process files naming a module that imports it directly, so `veri/fused_step.py` lists `test_fused_halves_process.py` ⟦criterion 3⟧
- [ ] CLAUDE.md "Testing idiom" and SCRIPTS.md's affected-suites.sh entry say which test files a `veri/<m>.py` change lists, graded by new rows ⟦criterion 4⟧
