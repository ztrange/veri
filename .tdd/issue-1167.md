# Plan for #1167 — run_suite.py exits 247 for a signal-killed suite and prints a traceback for a missing one, where run-suite.sh exited 128+N and named the suite

- [x] A suite killed by signal N after it printed its count line makes run-suite.sh exit 128+N ⟦criterion 1⟧
- [ ] A suite path that does not exist makes run-suite.sh print `<name>: never reached its count line` and `<name>: its output was empty` on stderr, with no traceback, and exit 1 ⟦criterion 2⟧
- [ ] A suite path that exists but is not executable makes run-suite.sh print `<name>: never reached its count line` and `<name>: its output was empty` on stderr, with no traceback, and exit 1 ⟦criterion 2⟧
