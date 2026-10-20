### `check --step` run from a subdirectory of the repository (the step recorded from the repository root) still exits 1, naming a changed test file outside the step's record; a medium case in a real git repository under tmp_path ⟦criterion 1⟧
- replace `_in_repository()`'s hand-rolled walk up from cwd with `git rev-parse --show-toplevel`, as the issue specifies. This is not duplication removal, and a later step (the exit-2-outside-a-repo criterion) will likely force it.
- `main` guards record mode's two `os.path.exists(".git")` checks and check mode's `_in_repository()` separately. They could share one repository test. The record-mode checks are code this cycle did not write.
### `check --step` run outside any git repository exits 2, with stderr naming the missing repository, rather than exiting 0 ⟦criterion 2⟧
- the `record` branch repeats `os.path.exists(".git")` twice, which is the same cwd-`.git` test this issue replaces. It is code the cycle did not write, so I did not change it.
