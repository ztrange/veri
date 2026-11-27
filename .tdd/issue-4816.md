# Plan for #4816 — refactor: process cases sit through real waits they can shrink — network bound, poll pauses, kill grace, fetch retries

- [x] `watch_runs` pauses `VERI_WATCH_POLL` seconds between polls (tunable, default 2) ⟦criterion 1⟧
- [x] the conductor's ref-lock fetch gives up after `VERI_FETCH_RETRIES` tries (tunable, default 60) ⟦criterion 1⟧
- [x] `test_stack_land_process.py`'s hung-fetch case bounds the network at ≤2 s ⟦criterion 2⟧
- [x] `test_watch_runs_process.py` runs with startup delay ≤1, `--max-wait` 1 and poll pause ≤0.1 ⟦criterion 2⟧
- [x] `test_run_conductor_process.py`'s ref-lock case runs with ≤6 fetch retries ⟦criterion 2⟧
- [x] `test_supervise_process.py`'s `run_hang_after_lock` runs with `VERI_TIMEOUT` ≤2 and delay ≤3 ⟦criterion 2⟧
- [ ] `test_stop_run_process.py`'s `test_3375_…` runs with kill grace ≤0.2 ⟦criterion 2⟧
- [ ] `test_branch_gate_process.py` and `test_pr_prepare_process.py` run with `VERI_POLL` ≤0.05 ⟦criterion 2⟧
