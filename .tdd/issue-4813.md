# Plan for #4813 — refactor: five process-test files build scratch repos through repo_builder.new_repo, and a ratchet stops new direct git init

- [x] `unit/test_direct_git_init.py` fails naming a test file under `tests/py/` that runs `git init` directly and is not on its shrink-only list, and fails naming a listed file that no longer does ⟦criterion 2⟧
- [x] `test_verify_process.py` runs no direct `git init`: its scratch repos come from `repo_builder.new_repo`, and it leaves the ratchet's list ⟦criterion 1⟧
- [x] `test_skill_edit_step_process.py` runs no direct `git init`, and leaves the ratchet's list ⟦criterion 1⟧
- [ ] `test_role_state_process.py` runs no direct `git init`, and leaves the ratchet's list ⟦criterion 1⟧
- [ ] `test_merge_lock.py` runs no direct `git init`, and leaves the ratchet's list ⟦criterion 1⟧
- [ ] `test_mutation_probe_process.py` runs no direct `git init`, and leaves the ratchet's list ⟦criterion 1⟧
