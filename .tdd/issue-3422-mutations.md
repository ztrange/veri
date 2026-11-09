file 39
skills/tdd/scripts/veri/queued_merge.py
old 39
"--rebase", "--match-head-commit", head
new 39
"--squash", "--match-head-commit", head
command 187
make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3422_queued_merge_of_a_pr_whose_body_carries_closes_for_the_runs_issue_merges_it_on_the_pushed_head_and_exits_0

before 40
ee0a2398e43a4d5c42af165b56820ad065f957c0
keep 53
skills/tdd/scripts/tests/py/unit/test_queued_merge.py
command 222
make test TESTS=skills/tdd/scripts/tests/py/unit/test_queued_merge.py::test_3422_queued_merge_of_a_pr_whose_only_closing_line_is_for_a_longer_issue_number_sharing_the_runs_number_as_a_prefix_exits_2_and_makes_no_merge_call

