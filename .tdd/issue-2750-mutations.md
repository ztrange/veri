file 33
skills/tdd/scripts/veri/status.py
old 96
        if i["state"] == "OPEN" and label in [x["name"] for x in i["labels"]]:
            for b
new 71
        if label in [x["name"] for x in i["labels"]]:
            for b
command 320
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpklyw6cwh/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_blocked.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_blocked.py::test_2750_report_queue_omits_blocked_issues_that_are_closed_or_not_opted_in

file 33
skills/tdd/scripts/veri/status.py
old 96
        if i["state"] == "OPEN" and label in [x["name"] for x in i["labels"]]:
            for b
new 50
        if i["state"] == "OPEN":
            for b
command 320
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpklyw6cwh/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_blocked.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_blocked.py::test_2750_report_queue_omits_blocked_issues_that_are_closed_or_not_opted_in

file 33
skills/tdd/scripts/veri/status.py
old 36
.stdout.strip() == first["started"]:
new 23
.stdout.strip() != "x":
command 348
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpklyw6cwh/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_running.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_running.py::test_2750_report_running_omits_a_journal_whose_conductor_start_pid_is_alive_but_started_at_another_time

