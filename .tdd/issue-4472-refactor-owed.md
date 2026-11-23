### With `branch` in `.tdd/issue-<n>-skip-verify`, `verify-branch.sh <n>` writes `skipped` to `.tdd/verdict-branch.exit` and exits 0 ⟦criterion 16⟧
- test-only | Duplicated Code: Extract Function — the worktree-setup lines in `test_verify_branch.py` repeat across the `test_4472_*` skip cases; a shared fixture would remove them
not-done | coupling | mutual reference: skills/tdd/scripts/veri/build_verify_prompt.py skills/tdd/scripts/veri/prompt_template.py
