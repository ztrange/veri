# Plan for #1193 — The pytest leg runs every case under a per-case timeout (pytest-timeout), and refuses a venv without it

- [x] requirements-dev.txt pins pytest-timeout to one exact version (`pytest-timeout==<x.y.z>`), as it pins pytest, and the Makefile never restates that version ⟦criterion 1⟧
- [x] In a scratch tree, a planted pytest case that sleeps past the leg's per-case timeout fails, named in the output as a timeout, while the leg still runs the tree's other cases (a passing case is reported passed) and the recipe reaches its result line, SUITES FAILED, under both `make unit` and `make test` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] With no override, the per-case timeout the pytest leg of `make unit` and `make test` applies to every case is 30 s ⟦criterion 1⟧
- [ ] When the leg's interpreter cannot import pytest_timeout, `make unit` and `make test` exit 2 before any suite runs, with stderr naming `pytest-timeout` and `make install-dev`; a stand-in variable, like `VERI_PYTEST_IMPORTABLE`, supplies the answer in place of asking the interpreter ⟦criterion 2⟧
- [ ] CLAUDE.md's `make install-dev` row says requirements-dev.txt installs pytest-timeout alongside pytest, and its pytest-leg paragraph states the 30 s per-case timeout and the pytest-timeout refusal with its stand-in variable ⟦diff-checked⟧ ⟦criterion 2⟧
