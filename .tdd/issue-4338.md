# Plan for #4338 — ensure-run-state-ignored.sh appends the pre-#4048 rule to main's .gitignore, so every run commits a change that reddens test_4048

- [ ] In a repo whose `.gitignore` holds the #4048 rule block, `ensure-run-state-ignored.sh` prints `already present` and leaves `.gitignore` byte-identical, pinned in `tests/py/test_ensure_run_state_ignored_process.py` ⟦criterion 1⟧
- [ ] In a repo with an unrelated `.gitignore`, the lines `ensure-run-state-ignored.sh` appends are the run-state rule lines main's `.gitignore` carries, so `git check-ignore` ignores run state and admits the five committed kinds, pinned in `tests/py/unit/test_ensure_run_state_ignored.py` ⟦criterion 2⟧
- [ ] `run-start.sh`'s step 1.4, in a tree whose `.gitignore` already holds the #4048 rule block, makes no `chore: ignore veri run state` commit, pinned in `tests/py/unit/test_run_start.py` ⟦criterion 3⟧
- [ ] `ready-check.sh`'s run-state-ignore fix for a partly carried rule names the rule's lines without calling them three
