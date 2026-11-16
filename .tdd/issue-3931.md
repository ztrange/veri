# Plan for #3931 — PRD 023.5: process cases copy one template repository

- [ ] a second `new_repo` in one worker makes its repository with no `init` call through `repo_builder.git` ⟦criterion 2⟧
- [ ] `new_repo`'s first and second call in one worker each return a repository on `<branch>` with no commit, no configured identity and a clean `git status` ⟦criterion 1⟧
- [ ] two repositories from `new_repo` share no file: a commit in one leaves the other with no commit ⟦criterion 3⟧
- [ ] the template `new_repo` copies lives under the run's `--basetemp` ⟦criterion 4⟧
- [ ] no case in `test_tests_frozen_process.py` runs `git init` itself; each calls `new_repo` ⟦criterion 5⟧
- [ ] no case in `test_pin_recheck_process.py` runs `git init` itself; each calls `new_repo` ⟦criterion 5⟧
