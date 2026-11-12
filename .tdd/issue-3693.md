# Plan for #3693 — dispatch.sh reports a freshly launched run as vanished while its conductor is still in preflight

- [x] With run N's conductor process alive in preflight, and neither `.tdd/wt/N` nor its `conductor.pid` written, `dispatch.sh` does not exit 2 with "vanished" across consecutive polls and keeps watching (a small unit case in `tests/py/unit/test_dispatch.py`, the process-liveness check faked in-process) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] With no worktree and no live conductor process for run N, `dispatch.sh` still exits 2 with `run N vanished: no worktree left behind` across consecutive polls (a small unit case in `tests/py/unit/test_dispatch.py`, the process-liveness check faked in-process to answer no process) ⟦criterion 2⟧
