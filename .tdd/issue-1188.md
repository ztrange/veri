# Plan for #1188 — detach-leaf.sh exits 0 when its command never started

- [x] detach-leaf.sh given a command path that does not exist exits 2, prints exactly one stderr line naming that command, and starts nothing ⟦criterion 1⟧
- [x] detach-leaf.sh given a command path that exists but cannot be executed (a directory) exits 2, prints exactly one stderr line naming that command, and starts nothing ⟦criterion 1⟧
- [ ] fix the CI failure: skills/tdd/scripts/tests/orchestrate.test.sh — FAIL - #1126 with SIGPIPE and SIGXFSZ at their defaults, a conductor still leads a new session whose pid orchestrate SIGTERMs, stdin /dev/null, stderr orchestrate's, SIGINT and SIGQUIT ignored (stderr diff: an extra 'Terminated' line, CI run 37820902833) ⟦ci-repair⟧ ⟦criterion 1⟧
