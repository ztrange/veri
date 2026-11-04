file 39
skills/tdd/scripts/veri/queued_merge.py
old 75
if _git(worktree, "merge-base", "--is-ancestor", lease, "HEAD").returncode:
new 9
if False:
command 189
make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3030_queued_merge_on_a_dirty_worktree_strictly_behind_origin_branch_exits_2_naming_it_and_never_rebases_or_pushes

