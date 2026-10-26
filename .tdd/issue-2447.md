# Plan for #2447 — One reused pid in a months-old tmpdir record stops every launch: sweep_dead_runs reads EPERM from os.kill as an error

- [ ] A `.tdd/issue-<n>-tmpdir-skill-commit` record whose pid exists but belongs to another user (`os.kill(pid, 0)` raises `PermissionError`) does not stop a launch: `run-conductor.sh` gets past the sweep, the record and its directory are left in place, and the launch goes on; the case fails on the current code (a small in-process case faking only the `os.kill` boundary) ⟦criterion 1⟧
- [ ] A tmpdir record whose pid is genuinely gone (`os.kill(pid, 0)` raises `ProcessLookupError`) still has its `veri-run-*` directory swept, so the fix does not turn the sweep off ⟦criterion 2⟧
- [ ] A `PermissionError` escaping a `veri/` entry point's `main` names the operation that raised it (the call, such as `os.kill`) in the refusal line `entry.py` prints, not only the exception class and message ⟦criterion 3⟧
- [ ] The first criterion's guard, broken on purpose by catching `PermissionError` as dead again, is watched going red and then restored ⟦human-owed⟧ ⟦criterion 4⟧
