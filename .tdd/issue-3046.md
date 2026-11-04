# Plan for #3046 — A pin-recheck before-state replay restores every touched file with its content but not its git mode

- [x] After a pin-recheck before-state replay, a touched file that was 100755 before the replay is 100755 after it with the same bytes, and a 100644 one stays 100644, pinned by one case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py (a process case, real git) that replays over an executable file absent at the before-sha and compares its git ls-files -s mode and bytes before and after ⟦criterion 1⟧
- [ ] Go-red control: with the mode restore removed, the case pinning the replay's mode restore goes red ⟦human-owed⟧ ⟦criterion 2⟧
