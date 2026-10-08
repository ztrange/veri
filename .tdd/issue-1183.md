# Plan for #1183 — verify.py exits 1 (read as REJECT) when a leaf leaves ~/.gitconfig unreadable, where verify.sh refused with exit 2

- [x] When reading `~/.gitconfig` before the verifier leaf is launched fails — it is a directory, or reading it raises any other OSError — `verify.sh` exits 2 with a stderr message naming the global git config, launches no leaf and prints no traceback; the existing cases that pin exit 1 for this path now expect 2 ⟦criterion 1⟧ ⟂ refactor pending
- [ ] When the verifier leaf leaves `~/.gitconfig` a directory after it ran, `verify.sh` exits 2 with a message naming the global git config and prints no traceback, never exit 1 ⟦criterion 1⟧
- [ ] When the verifier leaf leaves `~/.gitconfig` unreadable after it ran (reading it raises PermissionError or another OSError), `verify.sh` exits 2 with a message naming the global git config and prints no traceback ⟦criterion 1⟧
- [ ] When the verifier leaf moved HEAD and restoring it with `git update-ref HEAD <before>` exits non-zero, `verify.sh` exits 2, never the git status such as 128, with no traceback ⟦criterion 2⟧
- [ ] When the verifier leaf moved HEAD and git cannot be started to restore it, `verify.sh` exits 2 with no traceback ⟦criterion 2⟧
