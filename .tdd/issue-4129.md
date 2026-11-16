# Plan for #4129 — PRD 023.9: the supervisor reads its clocks in-process

- [x] tests/py/unit/test_supervise.py: with VERI_WALL_CLOCK set, `now()` runs that command split on spaces and returns its stdout, through `/bin/sh` when the command raises ENOEXEC; VERI_WALL_CLOCK is read through `tunables.read`, outside `TABLE` ⟦criterion 2⟧
- [x] tests/py/test_supervise_process.py: `run_queued_leaf_past_window` names its `date` stub in VERI_WALL_CLOCK instead of PATH, and the in-process cases that answered `["date"]` or `["stat"]` patch `supervise.now` and `supervise.mtime_of`; the `spelled` argv-order list is dropped and the verdict-leaf "no stat ran" check becomes a spy on `supervise.mtime_of` recording no call for a `verdict-*` leaf ⟦criterion 5⟧
- [x] tests/py/unit/test_supervise.py: `now()` returns `int(time.time())` as text when VERI_WALL_CLOCK is unset or empty ⟦criterion 1⟧
- [x] tests/py/unit/test_supervise.py: `mtime_of(path)` returns `int(os.stat(path).st_mtime)` as text, and `now()` when the file is missing ⟦criterion 3⟧
- [x] tests/py/unit/test_supervise.py: under `fake_processes`, `now()` with VERI_WALL_CLOCK unset and `mtime_of()` of an existing and of a missing file record no call ⟦criterion 4⟧
