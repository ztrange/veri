# Plan for #1188 — detach-leaf.sh exits 0 when its command never started

- [x] detach-leaf.sh given a command path that does not exist exits 2, prints exactly one stderr line naming that command, and starts nothing ⟦criterion 1⟧
- [ ] detach-leaf.sh given a command path that exists but cannot be executed (a directory) exits 2, prints exactly one stderr line naming that command, and starts nothing ⟦criterion 1⟧
