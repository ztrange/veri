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

before 40
4285b701485e92b52e4e98ea7609e33b4bcd161d
keep 48
skills/tdd/scripts/tests/py/unit/test_wait_ci.py
command 202
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_counts_an_on_map_holding_a_pull_request_key_as_triggering_and_the_same_map_without_it_as_not_when_ci_on_pr_is_unset_issue_2885
green 40
b3b0ba2e7fb3a3257370250c86d1dd9baa4b3074

before 40
4285b701485e92b52e4e98ea7609e33b4bcd161d
keep 48
skills/tdd/scripts/tests/py/unit/test_wait_ci.py
command 392
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp6exa3j5y/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_wait_ci.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_exits_0_warning_no_check_will_come_on_a_mergeable_pr_with_no_checks_when_ci_on_pr_is_unset_and_the_head_tree_has_only_workflow_call_and_schedule_workflows_issue_2885
green 40
8a361237f21a8efad62a6dfb26ea48fbe19facce

file 34
skills/tdd/scripts/veri/wait_ci.py
old 55
if state in ("none", "skipped") and mergeable is False:
new 114
if state in ("none", "skipped") and mergeable is False and (explicit or not no_pull_request_workflow(repo, head)):
command 225
make test TESTS=skills/tdd/scripts/tests/py/unit/test_wait_ci.py::test_main_still_exits_2_naming_the_conflict_on_a_conflicting_pr_with_no_checks_when_ci_on_pr_is_unset_and_the_head_tree_has_no_pull_request_workflow_issue_2885

