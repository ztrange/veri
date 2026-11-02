file 39
skills/tdd/scripts/veri/queued_merge.py
old 47
    if code:
        return code
    gh_merge =
new 168
    if code:
        return code
    code = _gate(pid, os.path.join(SCRIPTS, "detect-test-command.sh"), "--tier", "all")
    if code:
        return code
    gh_merge =
command 352
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp11tvabbv/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_queued_merge.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_2886_queued_merge_on_a_pr_with_no_checks_whose_rebase_leaves_head_unchanged_merges_without_running_the_full_test_command

file 39
skills/tdd/scripts/veri/queued_merge.py
old 45
    if code:
        return code
    gh_merge
new 114
    if code:
        return code
    _gate(pid, "detect-test-command.sh", "--tier", "all", keep=True)
    gh_merge
command 359
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp11tvabbv/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_queued_merge.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_2886_queued_merge_on_a_pr_with_checks_whose_rebase_moved_its_tip_merges_on_the_ci_verdict_without_running_the_full_test_command

