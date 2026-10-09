# Plan for #1244 — strip_session_env deletes a CLAUDE_BIN stub whose path contains the session id, so the real claude runs instead

- [x] strip_session_env keeps CLAUDE_BIN and every VERI_* variable whose value contains the session id, and still removes every other variable whose value carries it ⟦criterion 1⟧ ⟂ refactor pending
- [ ] run-conductor.sh, given a CLAUDE_BIN whose path contains CLAUDE_CODE_SESSION_ID, runs the binary CLAUDE_BIN names and hands that CLAUDE_BIN on in its environment, so the conductor's own leaves launch it too ⟦criterion 1⟧
