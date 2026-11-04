file 39
skills/tdd/scripts/veri/queued_merge.py
old 75
if _git(worktree, "merge-base", "--is-ancestor", lease, "HEAD").returncode:
new 9
if False:
command 189
make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3030_queued_merge_on_a_dirty_worktree_strictly_behind_origin_branch_exits_2_naming_it_and_never_rebases_or_pushes

before 40
78f40fa1ff8a378b63e6e3f2bd07941e9f464013
keep 53
skills/tdd/scripts/tests/py/unit/test_queued_merge.py
command 351
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpm668c7vo/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_queued_merge.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3030_queued_merge_on_a_clean_worktree_strictly_behind_origin_branch_whose_fast_forward_fails_exits_2_and_pushes_nothing
green 40
87f6d7cf0d903fbe3f04361f43484c32b118df7d

