# Plan for #936 — make install-dev never says to put the venv first on PATH, and the Python-version refusals don't name it

- [x] `make install-dev` that builds a fresh venv at $VERI_VENV ends its output with a line naming `$VERI_VENV/bin` and telling the reader to put it first on PATH ⟦criterion 1⟧
- [x] `make install-dev` that reuses an existing venv at $VERI_VENV meeting the floor also ends its output with the line naming `$VERI_VENV/bin` and telling the reader to put it first on PATH ⟦criterion 1⟧
- [x] `make install-dev` refusing — no interpreter on PATH meets the floor, or the existing venv is below it — exits 2 with its current message and prints no PATH line ⟦criterion 2⟧
- [x] `run-conductor.sh`, with the python3 on PATH below the floor and a venv at $VERI_VENV whose interpreter meets it, exits 2 and its stderr names `$VERI_VENV/bin` as what to put first on PATH ⟦criterion 3⟧
- [x] `leaf-launchable.sh`, with the python3 on PATH below the floor and a venv at $VERI_VENV whose interpreter meets it, exits 2 and its stderr names `$VERI_VENV/bin` as what to put first on PATH ⟦criterion 3⟧
- [x] `run-conductor.sh`, with the python3 on PATH below the floor and no venv at $VERI_VENV, exits 2 with today's message and names no venv path ⟦criterion 4⟧
- [ ] `leaf-launchable.sh`, with the python3 on PATH below the floor and no venv at $VERI_VENV, exits 2 with today's message and names no venv path ⟦criterion 4⟧
- [ ] `run-conductor.sh` and `leaf-launchable.sh`, with the python3 on PATH below the floor and a venv at $VERI_VENV whose own interpreter is also below the floor, exit 2 with today's message and name no venv path
- [ ] Every case `venv-python.test.sh`, `pytest-leg.test.sh` and `make-test-env.test.sh` already hold still passes with its assertions unchanged ⟦diff-checked⟧ ⟦criterion 5⟧
