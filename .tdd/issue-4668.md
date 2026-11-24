# Plan for #4668 — `/vinstall cloud`: prepare a repository so a Claude Code cloud session can run veri

- [x] cloud-install.sh on a repository with no `.claude/settings.json` creates it holding one `SessionStart` hook that runs `cloud-setup.sh` only when `CLAUDE_CODE_REMOTE=true` ⟦criterion 1⟧
- [x] cloud-install.sh on an existing `.claude/settings.json` adds the hook and keeps every existing key and hook ⟦criterion 1⟧
- [x] cloud-install.sh run a second time changes nothing and leaves one hook ⟦criterion 1⟧
- [x] cloud-install.sh on a `.claude/settings.json` that is not valid JSON exits 2 with a stderr line naming the file and leaves it unchanged ⟦criterion 2⟧
- [ ] cloud-install.sh on the repository holding veri's own scripts names `cloud-setup.sh` in the hook through `$CLAUDE_PROJECT_DIR`, not the local absolute path
- [ ] cloud-setup.sh exits 0 doing nothing when `CLAUDE_CODE_REMOTE` is not `true` ⟦criterion 3⟧
- [ ] cloud-setup.sh in a cloud session picks the first interpreter at or above `VENV_FLOOR`, runs the install, and writes the PATH line to `$CLAUDE_ENV_FILE` ⟦criterion 4⟧
- [ ] cloud-setup.sh called again with the same venv lock runs no install ⟦criterion 4⟧
- [ ] cloud-setup.sh with no interpreter at or above the floor and no `uv` exits 2 naming each interpreter tried and its version ⟦criterion 5⟧
- [ ] cloud-setup.sh with no interpreter at or above the floor but `uv` on PATH installs one with `uv` and uses it
- [ ] cloud-setup.sh runs its module on a python3 below `VENV_FLOOR`: its shim does not refuse
- [ ] `skills/vinstall/SKILL.md` has a `## Cloud sessions` section and `SCRIPTS.md` catalogues both scripts, graded by the issue's rows ⟦criterion 6⟧
