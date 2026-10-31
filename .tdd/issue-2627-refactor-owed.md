### When the run's worktree is cut during the run, a conductor that exits non-zero (a bail) leaves the pinned `skills/tdd/scripts` under the worktree's `.tdd/`, at the commit in `.tdd/issue-<n>-skill-commit`, and a script in the copy runs ⟦criterion 1⟧
- test-only | extract the duplicated clone/repo seeding (`commit_all`, pin lookup) and the `run_conductor.main` subprocess invocation in test_run_conductor_process.py into shared helpers
### A launch that re-pins with `VERI_NEW_SKILL=1` over a worktree already holding a copy leaves only the newly pinned commit's scripts in that copy, so the copy never disagrees with `.tdd/issue-<n>-skill-commit` ⟦criterion 1⟧
- test-only | the new cases in `test_run_conductor_process.py` may share setup that could move into a helper or fixture (not inspected in detail)
### `git add -A` in a run's worktree holding the pinned copy stages nothing from the copy ⟦criterion 1⟧
- test-only | extract the repeated skill-clone/repo/worktree setup, the `git` helper and the run_conductor subprocess launch shared by the four #2627 cases into fixtures or helpers
### `$S/pinned-scripts.sh <n>` prints the directory holding run `<n>`'s pinned scripts under the run's worktree `.tdd/`, exit 0 ⟦criterion 3⟧
- test-only | extract the repeated `subprocess.run([... "pinned-scripts.sh" ...], env={PATH, PYTHONDONTWRITEBYTECODE})` call in test_pinned_scripts_process.py into one helper
### Run from the main checkout with the directory absent, `pinned-scripts.sh <n>` names the commit from the main checkout's `.tdd/issue-<n>-skill-commit`, the file `run_conductor.py` records the pin in, and exits 2 with the `git archive <pin> skills/tdd/scripts` recovery line ⟦added⟧ ⟦criterion 3⟧
- test-only | extract the repeated subprocess.run call and env in test_pinned_scripts_process.py into one helper
### With that directory absent and no pin recorded, `pinned-scripts.sh <n>` exits 2 saying no pin is recorded, and never prints the installed copy's path ⟦criterion 3⟧
- test-only | hoist the repeated subprocess.run call and env dict in test_pinned_scripts_process.py into a helper
