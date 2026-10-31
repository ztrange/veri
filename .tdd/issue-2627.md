# Plan for #2627 — A run's pinned script copy disappears from its tmpdir, so operator recovery silently falls back to whatever is installed

- [x] When the run's worktree already exists at launch, `run-conductor.sh` extracts the pinned `skills/tdd/scripts` under that worktree's `.tdd/` before the conductor process starts, so a conductor killed by SIGKILL still leaves the copy (a medium case, with a real process and a real SIGKILL) ⟦criterion 4⟧
- [x] When the run's worktree is cut during the run, a conductor that exits non-zero (a bail) leaves the pinned `skills/tdd/scripts` under the worktree's `.tdd/`, at the commit in `.tdd/issue-<n>-skill-commit`, and a script in the copy runs ⟦criterion 1⟧
- [x] A launch that re-pins with `VERI_NEW_SKILL=1` over a worktree already holding a copy leaves only the newly pinned commit's scripts in that copy, so the copy never disagrees with `.tdd/issue-<n>-skill-commit` ⟦criterion 1⟧
- [x] `git add -A` in a run's worktree holding the pinned copy stages nothing from the copy ⟦criterion 1⟧
- [x] `issue-worktree.sh --remove <n>` on a clean worktree holding the pinned copy succeeds and the copy is gone with the worktree ⟦criterion 2⟧
- [x] A skill snapshot a SIGKILLed conductor left outside the worktree is removed by `issue-worktree.sh --remove <n>`, so no copy for the run is left anywhere once the worktree is removed ⟦criterion 2⟧
- [x] `$S/pinned-scripts.sh`, added as a `/bin/sh` shim over a `veri/` module, prints a usage line and exits 2 with no argument ⟦criterion 3⟧
- [x] `$S/pinned-scripts.sh <n>` prints the directory holding run `<n>`'s pinned scripts under the run's worktree `.tdd/`, exit 0 ⟦criterion 3⟧
- [x] With that directory absent and a pin recorded, `pinned-scripts.sh <n>` exits 2 naming the pinned commit from `.tdd/issue-<n>-skill-commit` and the `git archive <pin> skills/tdd/scripts` recovery line, and never prints the installed copy's path ⟦criterion 3⟧
- [x] Run from the main checkout with the directory absent, `pinned-scripts.sh <n>` names the commit from the main checkout's `.tdd/issue-<n>-skill-commit`, the file `run_conductor.py` records the pin in, and exits 2 with the `git archive <pin> skills/tdd/scripts` recovery line ⟦added⟧ ⟦criterion 3⟧
- [x] With that directory absent and no pin recorded, `pinned-scripts.sh <n>` exits 2 saying no pin is recorded, and never prints the installed copy's path ⟦criterion 3⟧
- [x] Run from a checkout holding no `.tdd` directory at all, with the directory absent, `pinned-scripts.sh <n>` exits 2 saying no pin is recorded and prints no path, never a directory that does not exist ⟦added⟧ ⟦criterion 3⟧
- [ ] Unit skills/tdd/SCRIPTS.md takes the issue's SC59 row: the catalogue's `$S/pinned-scripts.sh` entry ⟦skill-edit⟧ ⟦criterion 3⟧
