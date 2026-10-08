# Plan for #1130 — orchestrate.sh with a broken stdout exits outside the exit contract and leaves its conductor running

- [x] with its stdout a pipe whose reader has exited, orchestrate.sh exits 2 with one stderr line saying its stdout is gone and no traceback, where it now lets BrokenPipeError escape ⟦criterion 1⟧
- [x] with its stdout closed (sys.stdout is None), orchestrate.sh exits 2 with the same one stderr line and no traceback, where it now carries on ⟦criterion 2⟧
- [x] when its stdout breaks — a pipe whose reader has exited, or closed — the conductor orchestrate.sh launched is stopped by SIGTERM to its process group before orchestrate.sh exits ⟦criterion 3⟧
- [ ] when its stdout breaks — a pipe whose reader has exited, or closed — solvable-issues.sh is asked no further time after the break ⟦criterion 4⟧
- [ ] orchestrate.sh's header lists a broken stdout among the causes of exit 2 ⟦diff-checked⟧
