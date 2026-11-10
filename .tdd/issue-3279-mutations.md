file 39
skills/tdd/scripts/veri/report_cache.py
old 17
timedelta(days=7)
new 18
timedelta(days=60)
context 111
    week_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
command 168
make test TESTS=skills/tdd/scripts/tests/py/unit/test_report_cache.py::test_refresh_fetches_comments_of_an_issue_closed_6_days_ago_and_not_of_one_closed_8_days_ago_3279

file 39
skills/tdd/scripts/veri/report_cache.py
old 17
timedelta(days=7)
new 17
timedelta(days=1)
context 111
    week_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
command 168
make test TESTS=skills/tdd/scripts/tests/py/unit/test_report_cache.py::test_refresh_fetches_comments_of_an_issue_closed_6_days_ago_and_not_of_one_closed_8_days_ago_3279

