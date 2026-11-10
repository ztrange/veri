file 33
skills/tdd/scripts/veri/status.py
old 52
not any(t.endswith("(%s)" % name) for t in subjects)
new 36
not any(name in t for t in subjects)
context 83
        if pr is not None and not any(t.endswith("(%s)" % name) for t in subjects):
command 156
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_waiting.py::test_3250_report_waiting_lists_a_pr_whose_issue_subject_is_not_on_local_main

file 33
skills/tdd/scripts/veri/status.py
old 52
not any(t.endswith("(%s)" % name) for t in subjects)
new 5
False
context 83
        if pr is not None and not any(t.endswith("(%s)" % name) for t in subjects):
command 156
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_waiting.py::test_3250_report_waiting_lists_a_pr_whose_issue_subject_is_not_on_local_main

