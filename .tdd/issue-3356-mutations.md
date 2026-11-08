file 35
skills/tdd/scripts/veri/dispatch.py
old 60
return "MERGED" if pull["merged"] else pull["state"].upper()
new 15
return "CLOSED"
command 199
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_prints_nothing_and_keeps_looping_when_a_vanished_queued_merge_url_answers_a_200_body_merged_true_through_gh_api_issue_3356

