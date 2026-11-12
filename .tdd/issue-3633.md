# Plan for #3633 — run_conductor.py allows a second conductor on an issue whose pid file names a live conductor

- [x] Launching `run_conductor.py N` while the run worktree's `.tdd/conductor.pid` names a live process (the pid answers `kill -0` and its recorded start time matches) exits non-zero before launching any `claude`, names that pid on stderr, and leaves the pid file byte-for-byte unchanged ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `restart-conductor.sh N` does not relaunch the conductor (no `detach_leaf` call) when the run's `.tdd/conductor.pid` is unreadable while a `run_conductor.py N` process is live: an unreadable pid file with such a process reads as unknown, not as a dead conductor ⟦criterion 2⟧
