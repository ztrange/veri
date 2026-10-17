# Plan for #1641 — The fast-tier guard misses aliased and os/pty process starts; its exemption table needs relative keys, real reasons and stale-entry checks

- [x] Each process-start form — `from os import system`, `import os as o; o.system(…)`, `from pty import spawn`, `os.popen`, `os.posix_spawn` — planted in a fast-tier test file is reported by the guard naming `file:line`, and the message names the actual call (`os.system`, `pty.spawn`, `os.popen`, `os.posix_spawn`, …) rather than "through subprocess"; pinned by one parametrized pytest case over the five forms ⟦criterion 1⟧
- [x] The guard's exemption table is keyed by a `file:line` whose file is a path relative to `tests/py/` (the root the guard is given), so an entry suppresses the offence it names whatever absolute directory the tree lives in; pinned by one case ⟦criterion 2⟧
- [ ] An exemption-table entry whose reason is empty or only whitespace is refused, naming the entry; pinned by one case ⟦criterion 2⟧
- [ ] An exemption-table entry that matches no file under the guard's root makes the guard fail naming that entry; pinned by one case ⟦criterion 2⟧
- [ ] A test file that runs another suite by passing the suite path as a keyword argument (`path="…/test_x.py"`) is reported as a nested suite naming `file:line`; pinned by one case ⟦criterion 3⟧
