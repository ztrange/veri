# Plan for #2354 — make test inherits the Mac's TMPDIR, so a failure that needs CI's /tmp passes every local check

- [x] The pytest leg's environment setup (`veri/pytest_leg.py`, the leg `make test` and `make unit` launch) gives its cases `/tmp` as the inherited TMPDIR when the host's TMPDIR is set elsewhere, pinned by a small in-process case that runs the leg's environment setup with TMPDIR set to another directory and observes TMPDIR `/tmp` in the environment the cases inherit ⟦criterion 1⟧
- [ ] The Makefile's pycache default (`${TMPDIR:-/tmp}/veri-pycache-<uid>`, used when `VERI_PYCACHE` is unset) is left unchanged by the branch and still resolves from the host's own TMPDIR, since it is computed before the leg runs ⟦diff-checked⟧ ⟦criterion 2⟧
