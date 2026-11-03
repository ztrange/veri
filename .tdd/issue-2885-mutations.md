file 34
skills/tdd/scripts/veri/wait_ci.py
old 17
unless_empty="1")
new 17
unless_empty="0")
command 210
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_keeps_its_wait_with_3_on_a_mergeable_pr_with_no_checks_when_ci_on_pr_is_unset_and_the_head_tree_has_a_pull_request_workflow_issue_2885

file 34
skills/tdd/scripts/veri/wait_ci.py
old 25
if "pull_request" in text
new 59
if "pull_request" in text.replace("pull_request_target","")
command 222
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_keeps_its_wait_with_3_on_a_mergeable_pr_with_no_checks_when_ci_on_pr_is_unset_and_the_head_tree_has_only_a_pull_request_target_workflow_issue_2885

before 40
4285b701485e92b52e4e98ea7609e33b4bcd161d
keep 48
skills/tdd/scripts/tests/py/unit/test_wait_ci.py
command 194
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_counts_a_trigger_list_holding_pull_request_as_triggering_and_a_push_only_list_as_not_when_ci_on_pr_is_unset_issue_2885
green 40
ea1c9cbab197d6960e63d6814b4bc78b7f6f776e

