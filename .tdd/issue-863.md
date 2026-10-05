# Plan for #863 — make install-dev builds its venv from a python3 below veri's 3.12 floor

- [x] with python3 below the floor and python3.12 on PATH, make install-dev builds the venv with python3.12, so the venv's interpreter reports a version at or above the floor ⟦criterion 1⟧
- [x] with python3 and python3.12 below the floor and python3.13 on PATH, make install-dev builds the venv with python3.13, the versioned candidates being tried newest first: python3.13 before python3.12 ⟦added⟧ ⟦criterion 1⟧
- [x] with python3 at or above the floor, make install-dev builds the venv with python3, as it does today ⟦criterion 2⟧
- [x] with no candidate on PATH meeting the floor, make install-dev exits 2, its stderr names the floor, and no venv is created at $VERI_VENV ⟦criterion 3⟧
- [x] with an existing venv at $VERI_VENV whose interpreter is below the floor, make install-dev exits 2, its stderr names the venv's path, its version and the floor, and the venv is left in place, neither reused for pip install nor deleted ⟦criterion 4⟧
- [x] install-dev's candidate list is derived from the one floor definition in lib/venv-python.sh: raising that definition to 3.13 alone drops python3.12 from the candidates install-dev tries ⟦criterion 5⟧
- [x] the pytest leg's floor check in the Makefile reads the same floor definition: raising that definition alone makes the leg refuse an interpreter it accepted before, naming the new floor ⟦criterion 5⟧
- [x] every case pytest-leg.test.sh and make-test-env.test.sh already hold keeps its assertions unchanged on this branch ⟦diff-checked⟧ ⟦criterion 6⟧
- [x] every case pytest-leg.test.sh and make-test-env.test.sh already hold passes ⟦full-suite⟧ ⟦criterion 6⟧
