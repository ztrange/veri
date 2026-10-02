# Plan for #621 — Leaves of an interactive /tdd inherit the conductor's Claude Code session, including auto-backgrounding

- [x] run-leaf.sh, run with CLAUDECODE, CLAUDE_CODE_SESSION_ID, CLAUDE_CODE_HOST_SESSION_ID, CLAUDE_CODE_MESSAGING_SOCKET, CLAUDE_CODE_MESSAGING_TOKEN, CLAUDE_PID, CLAUDE_CODE_CHILD_SESSION and CLAUDE_CODE_ENTRYPOINT all set, starts a stub claude (via CLAUDE_BIN) whose recorded environment contains none of them ⟦criterion 1⟧
- [x] run-leaf.sh and run-conductor.sh strip the session variables from one shared list, so a variable added to that list is absent from both the leaf's and the conductor's stub claude environment ⟦added⟧ ⟦criterion 1⟧
- [x] run-leaf.sh, run with CLAUDE_AUTO_BACKGROUND_TASKS=true set, starts a stub claude whose recorded environment does not contain CLAUDE_AUTO_BACKGROUND_TASKS ⟦criterion 2⟧ ⟂ refactor pending
- [ ] a leaf launched as supervise.sh <name> run-leaf.sh <prompt-file>, with all nine session variables set in the caller, starts a stub claude whose recorded environment contains none of them ⟦criterion 3⟧
- [ ] run-leaf.sh still passes every other variable through: a stub claude records VERI_TEST_CMD with the caller's value, and records GIT_CONFIG_GLOBAL as set ⟦criterion 4⟧
- [ ] run-leaf.sh, run with none of the nine session variables set, still exits with the stub's own exit code (0-3, else 2) and prints the same stdout as before ⟦criterion 5⟧
- [ ] run-conductor.sh, run with CLAUDE_AUTO_BACKGROUND_TASKS=true set, starts a stub claude whose recorded environment does not contain it, and the eight variables it already strips are still absent ⟦criterion 6⟧
