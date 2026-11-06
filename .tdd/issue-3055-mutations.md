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

