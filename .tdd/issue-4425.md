# Plan for #4425 — affected-suites.sh lists a ported module's process test file in the changed tier

- [x] a `veri/<m>.py` change lists `tests/py/test_<m>_process.py` when it exists, besides `test_<m>.py` and `unit/test_<m>.py` ⟦criterion 1⟧
- [x] a `<name>.sh` shim change lists `tests/py/test_<name with underscores>_process.py` when it exists ⟦criterion 2⟧
- [x] a ported module or shim change lists every `tests/py/test_*_process.py` that imports or runs it by name (`veri.<m>`, `<m>.py`, `<m>.sh`), and a process file naming neither lists nothing ⟦criterion 3⟧
- [x] a module no process file names lists the process files naming a module that imports it directly, so `veri/fused_step.py` lists `test_fused_halves_process.py` ⟦criterion 3⟧
- [x] CLAUDE.md "Testing idiom" and SCRIPTS.md's affected-suites.sh entry say which test files a `veri/<m>.py` change lists, graded by new rows ⟦criterion 4⟧
- [x] a changed `veri/<m>.py` lists every process test file running a `skills/tdd/scripts/*.sh` shim whose exec line names `veri/<m>.py`, whatever the shim is called ⟦criterion 3⟧
