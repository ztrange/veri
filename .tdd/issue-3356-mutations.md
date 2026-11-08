file 35
skills/tdd/scripts/veri/dispatch.py
old 60
return "MERGED" if pull["merged"] else pull["state"].upper()
new 15
return "CLOSED"
command 199
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_nothing_and_keeps_looping_when_a_vanished_queued_merge_url_answers_a_200_body_merged_true_through_gh_api_issue_3356

file 35
skills/tdd/scripts/veri/dispatch.py
old 31
not in ("MERGED", "UNRESOLVED")
new 41
not in ("MERGED", "UNRESOLVED", "CLOSED")
command 204
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_merge_failed_and_exits_0_when_a_vanished_queued_merge_url_answers_a_200_body_closed_not_merged_through_gh_api_issue_3356

