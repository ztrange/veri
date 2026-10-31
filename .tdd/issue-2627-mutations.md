file 41
skills/tdd/scripts/veri/issue_worktree.py
old 23
"status", "--porcelain"
new 36
"status", "--porcelain", "--ignored"
command 330
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdb649nzf/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_issue_worktree.py make test TESTS=skills/tdd/scripts/tests/py/test_issue_worktree.py::test_remove_of_a_clean_worktree_holding_the_pinned_scripts_copy_succeeds_and_the_copy_goes_with_it_issue_2627

file 41
skills/tdd/scripts/veri/issue_worktree.py
old 40
if removed.returncode == 0 and snapshot:
new 12
if snapshot:
command 339
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdb649nzf/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_issue_worktree.py make test TESTS=skills/tdd/scripts/tests/py/test_issue_worktree.py::test_main_remove_leaves_the_snapshot_directory_outside_the_worktree_in_place_when_git_worktree_remove_fails_issue_2627

file 41
skills/tdd/scripts/veri/issue_worktree.py
old 43
shutil.rmtree(snapshot, ignore_errors=True)
new 23
shutil.rmtree(snapshot)
command 316
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdb649nzf/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_issue_worktree.py make test TESTS=skills/tdd/scripts/tests/py/test_issue_worktree.py::test_main_remove_still_succeeds_when_the_recorded_snapshot_directory_is_already_gone_issue_2627

