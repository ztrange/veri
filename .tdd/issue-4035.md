# Plan for #4035 — PRD 025.1: the CI workflow and the Makefile describe today's suite

- [x] the gates job's `timeout-minutes` comment states 10 minutes, the 245-381 s measured on 2026-11-11 it was set against, and names #3653 for the history, with no 5- or 8-minute paragraph and no bash 3.2, plain-shell or suite count in ci.yml ⟦criterion 1⟧ ⟦criterion 3⟧
- [ ] the Makefile's first comment names `skills/tdd/` and its bash-floor comment says the suites are pytest files started by `pytest_leg.py`, bash 5 being needed for `lib/venv-python.sh` and the launches `launch_floor.py` guards ⟦criterion 2⟧ ⟦criterion 3⟧
- [ ] `CLAUDE.md`'s opening paragraph names the scripts as Python modules behind `/bin/sh` shims, graded by CM1 and CM4 reworded ⟦criterion 5⟧
