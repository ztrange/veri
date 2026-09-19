# Plan for #338 — detect-test-command.sh reads a target repo's declared fast/all test commands

- [x] With no `--tier` flag, detect-test-command.sh behaves exactly as today across every existing single-command case (`.veri/test-command`, package.json, Makefile, pytest/pyproject/setup.cfg, go.mod, Cargo.toml, tests/test_*.py glob, `--issue` override) ⟦criterion 1⟧
- [x] With no `--tier` flag, `veri: fast tests:` / `veri: all tests:` lines in the target's root CLAUDE.md are ignored and the single-command chain still answers ⟦criterion 1⟧
- [x] With both CLAUDE.md marker lines present and no issue override, `--tier fast` prints the fast command and `--tier all` prints the all command, byte for byte ⟦criterion 3⟧
- [x] A `veri: fast tests:` / `veri: all tests:` marker is recognized anywhere on a CLAUDE.md line, and one quoted inside a backtick span is skipped exactly as the issue override marker is ⟦criterion 2⟧
- [x] With neither CLAUDE.md marker line present, both `--tier fast` and `--tier all` resolve to the same single command the existing precedence chain picks ⟦criterion 4⟧
- [x] With only `veri: all tests:` declared, `--tier fast` falls back to the single-command chain rather than erroring or printing nothing ⟦criterion 5⟧
- [x] An `--issue` body override answers `--tier all` ahead of CLAUDE.md's `veri: all tests:`, while `--tier fast` in the same invocation still resolves from `veri: fast tests:` or, absent it, the single-command fallback ⟦criterion 6⟧
- [x] veri's own root CLAUDE.md declares `veri: fast tests: make unit` and `veri: all tests: make test`, so run from veri's repo root `--tier fast` prints `make unit` and `--tier all` prints `make test` ⟦criterion 7⟧
