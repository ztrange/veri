before 40
53149a93e6b490a7e658b5158460015e6ec1785d
keep 55
skills/tdd/scripts/tests/py/test_ready_check_process.py
command 164
make test TESTS=skills/tdd/scripts/tests/py/test_ready_check_process.py::test_issue_3055_ready_check_reads_the_pull_request_workflow_at_the_branch_origin_head_names

file 38
skills/tdd/scripts/veri/ready_check.py
old 62
return head.stdout.strip() if head.returncode == 0 else "main"
new 13
return "main"
command 164
make test TESTS=skills/tdd/scripts/tests/py/test_ready_check_process.py::test_issue_3055_ready_check_reads_the_pull_request_workflow_at_the_branch_origin_head_names

before 40
53149a93e6b490a7e658b5158460015e6ec1785d
keep 55
skills/tdd/scripts/tests/py/test_ready_check_process.py
command 332
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp0_txoya8/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_ready_check_process.py make test TESTS=skills/tdd/scripts/tests/py/test_ready_check_process.py::test_issue_3055_ready_check_given_a_repo_root_that_does_not_exist_exits_2_naming_not_a_git_repository

before 40
53149a93e6b490a7e658b5158460015e6ec1785d
keep 55
skills/tdd/scripts/tests/py/test_ready_check_process.py
command 334
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp0_txoya8/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_ready_check_process.py make test TESTS=skills/tdd/scripts/tests/py/test_ready_check_process.py::test_issue_3055_ready_check_with_unusable_repo_api_output_fails_the_push_access_row_instead_of_crashing

file 38
skills/tdd/scripts/veri/ready_check.py
old 41
except (ValueError, KeyError, TypeError):
new 18
except ValueError:
command 176
make test TESTS=skills/tdd/scripts/tests/py/test_ready_check_process.py::test_issue_3055_ready_check_with_unusable_repo_api_output_fails_the_push_access_row_instead_of_crashing

before 40
53149a93e6b490a7e658b5158460015e6ec1785d
keep 55
skills/tdd/scripts/tests/py/test_ready_check_process.py
command 346
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp0_txoya8/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_ready_check_process.py make test TESTS=skills/tdd/scripts/tests/py/test_ready_check_process.py::test_issue_3055_ready_check_where_every_row_holds_leaves_tree_index_and_refs_unchanged_and_makes_no_writing_gh_call

