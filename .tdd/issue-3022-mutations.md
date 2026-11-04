file 39
skills/tdd/scripts/veri/queued_merge.py
old 56
        if code:
            return code
    head = _rev
new 149
        if code:
            _gate(pid, "git", "-C", worktree, "update-index", "--really-refresh", keep=True)
            return code
    head = _rev
command 243
make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3022_queued_merge_whose_rebase_stops_with_would_be_overwritten_on_a_really_dirty_tree_fails_with_gits_code_keeps_the_lock_and_neither_refreshes_the_index_nor_continues

file 39
skills/tdd/scripts/veri/queued_merge.py
old 27
(("rebase", "origin/main"),
new 65
(("update-index", "--really-refresh"), ("rebase", "origin/main"),
command 228
make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3022_queued_merge_whose_rebase_stops_on_a_real_conflict_fails_with_gits_code_keeps_the_lock_pushes_nothing_and_neither_refreshes_the_index_nor_continues

