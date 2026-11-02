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

file 33
skills/tdd/scripts/veri/status.py
old 24
for l in f if l.strip()]
new 11
for l in f]
command 379
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpklyw6cwh/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_running_latest_start.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_running_latest_start.py::test_2750_report_running_lists_a_live_run_whose_conductor_start_is_followed_by_other_events_and_a_blank_line

file 33
skills/tdd/scripts/veri/status.py
old 36
name += " | total | $%.2f" % dollars
new 35
name += " | cost | $%.2f" % dollars
command 336
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpklyw6cwh/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_running_cost.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_running_cost.py::test_2750_report_running_block_labels_the_summed_dollars_with_the_total_row_label

file 33
skills/tdd/scripts/veri/status.py
old 16
if "model" in e:
new 8
if True:
command 330
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpklyw6cwh/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_running_models.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_running_models.py::test_2750_report_running_block_skips_a_launch_event_with_no_model_field

