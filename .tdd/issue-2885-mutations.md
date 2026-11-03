file 34
skills/tdd/scripts/veri/wait_ci.py
old 17
unless_empty="1")
new 17
unless_empty="0")
command 210
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_keeps_its_wait_with_3_on_a_mergeable_pr_with_no_checks_when_ci_on_pr_is_unset_and_the_head_tree_has_a_pull_request_workflow_issue_2885

