# Plan for #66 — Recognise a setup.cfg [tool:pytest] section as a pytest repo in detect-test-command.sh

- [x] a repo containing only a `setup.cfg` with a `[tool:pytest]` section prints `pytest -q` and exits 0
- [x] a repo containing only a `setup.cfg` with no `[tool:pytest]` section (for example just `[metadata]`) still exits 3 with nothing on stdout
- [ ] precedence is unchanged: a Makefile `test:` target still beats a `[tool:pytest]` setup.cfg, and a `[tool:pytest]` setup.cfg still beats a `go.mod`
