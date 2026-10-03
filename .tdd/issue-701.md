# Plan for #701 — The venv python3 lookup lives in one place

- [ ] skills/tdd/scripts/lib/venv-python.sh names the venv directory ($VERI_VENV, or ~/.veri-tools/venv when VERI_VENV is unset) and the interpreter: that directory's bin/python3 when it is executable, else the python3 on PATH ⟦criterion 2⟧
- [ ] run-suite.sh, the Makefile's test/unit recipe and its VENV_DIR, and the one lookup line of count-line-guard.test.sh take the venv lookup from lib/venv-python.sh, the only file among Makefile, skills/tdd/scripts/*.sh, skills/tdd/scripts/lib/*.sh and count-line-guard.test.sh that spells veri-tools/venv ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] run-suite.sh over a tests/py/test_*.py file runs $VERI_VENV/bin/python3 when it is present and the python3 on PATH when it is absent ⟦criterion 2⟧
- [ ] make test's pytest leg runs $VERI_VENV/bin/python3 when it is present and the python3 on PATH when it is absent ⟦criterion 2⟧
- [ ] make install-dev creates the environment at $VERI_VENV, or at ~/.veri-tools/venv when VERI_VENV is unset ⟦criterion 3⟧
- [ ] count-line-guard.test.sh and pytest-leg.test.sh are unmodified on this branch except the one lookup line of count-line-guard.test.sh that the lookup replaces ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 5⟧
