# Plan for #1225 — An issue's Test command overrides the full tier even when it names the repo's fast tier, so make test never runs locally

Choice for criterion 1: the full tier does not take the issue's line and resolves as it would with no issue line (no preflight refusal).

- [x] Run as `detect-test-command.sh --tier all --issue <body> <root>`, an issue whose `Test command:` equals the command `--tier fast` resolves to for that root (CLAUDE.md's `veri: fast tests:`) prints CLAUDE.md's `veri: all tests:` command, exit 0 ⟦criterion 1⟧
- [x] Run as `detect-test-command.sh --tier all --issue <body> <root>` with a root whose CLAUDE.md declares `veri: fast tests:` but no `veri: all tests:` line, an issue whose `Test command:` equals that fast command prints what the usual detection finds with no issue line (a Makefile `test:` target gives `make test`), exit 0 ⟦criterion 1⟧
- [ ] Run as `detect-test-command.sh --tier all --issue <body> <root>`, an issue whose `Test command:` differs from the command `--tier fast` resolves to prints the issue's command, exit 0 ⟦criterion 2⟧
- [ ] The cases this branch adds for the steps above run `detect-test-command.sh` through its entry point, not `decide()` in-process ⟦diff-checked⟧ ⟦criterion 3⟧
