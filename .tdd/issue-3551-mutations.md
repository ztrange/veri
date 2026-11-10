before 40
d38d8e031cfdabf502706b757752b9a3d07ad6b1
keep 62
skills/tdd/scripts/tests/py/unit/test_dispatch_issue_states.py
command 178
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch_issue_states.py::test_issue_states_reads_closed_issues_beyond_the_default_page_and_omits_an_unlisted_one_issue_3551

file 35
skills/tdd/scripts/veri/dispatch.py
old 37
"--state", "all", "--limit", "1000", 
new 0

context 108
    listed = json.loads(github.gh_issue_list("--state", "all", "--limit", "1000", "--json", "number,state"))
command 178
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch_issue_states.py::test_issue_states_reads_closed_issues_beyond_the_default_page_and_omits_an_unlisted_one_issue_3551

