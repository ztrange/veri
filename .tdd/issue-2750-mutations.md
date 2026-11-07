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

before 40
4dede5fe1f11c8821320cb83b7bc654b3f5a5b6a
keep 66
skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py
command 401
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpzy3raajk/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py::test_2750_report_queue_count_with_no_entry_in_status_last_prints_no_delta make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py::test_2750_report_queue_count_with_no_entry_in_status_last_prints_no_delta

file 33
skills/tdd/scripts/veri/status.py
old 76
    if label in last:
        text += " %+d" % (len(opted_in) - last[label])
new 57
    text += " %+d" % (len(opted_in) - last.get(label, 0))
command 157
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py::test_2750_report_queue_count_with_no_entry_in_status_last_prints_no_delta

before 40
4dede5fe1f11c8821320cb83b7bc654b3f5a5b6a
keep 66
skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py
command 431
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpzy3raajk/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py::test_2750_report_queue_with_status_last_holding_no_queue_key_prints_no_delta_and_exits_0 make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py::test_2750_report_queue_with_status_last_holding_no_queue_key_prints_no_delta_and_exits_0

file 33
skills/tdd/scripts/veri/status.py
old 29
json.load(f).get("queue", {})
new 21
json.load(f)["queue"]
command 172
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_queue_delta.py::test_2750_report_queue_with_status_last_holding_no_queue_key_prints_no_delta_and_exits_0

before 40
12c7e7930def08f9f0cb26d94579f6c7e23a0556
keep 64
skills/tdd/scripts/tests/py/unit/test_status_report_nojournal.py
command 323
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpclocydze/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_nojournal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_nojournal.py::test_2750_report_does_not_note_a_live_conductor_pid_run_that_has_a_journal

file 33
skills/tdd/scripts/veri/status.py
old 39
if n not in seen and recorded_alive(wt)
new 21
if recorded_alive(wt)
command 156
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_nojournal.py::test_2750_report_does_not_note_a_live_conductor_pid_run_that_has_a_journal

before 40
12c7e7930def08f9f0cb26d94579f6c7e23a0556
keep 64
skills/tdd/scripts/tests/py/unit/test_status_report_eta_range.py
command 333
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpclocydze/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_eta_range.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_eta_range.py::test_2750_report_queue_eta_range_scales_each_quartile_by_the_number_of_queued_issues

before 40
12c7e7930def08f9f0cb26d94579f6c7e23a0556
keep 64
skills/tdd/scripts/tests/py/unit/test_status_report_eta_range.py
command 344
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpclocydze/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_eta_range.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_eta_range.py::test_2750_report_queue_eta_skips_journals_without_a_done_event_and_an_empty_queue_prints_no_eta

before 40
12c7e7930def08f9f0cb26d94579f6c7e23a0556
keep 67
skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py
command 321
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpclocydze/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py::test_2750_report_that_failed_to_print_leaves_status_last_as_it_was

file 33
skills/tdd/scripts/veri/status.py
old 49
    if list(argv) == ["--report"]:
        print(
new 171
    if list(argv) == ["--report"]:
        os.makedirs(os.path.dirname(status_last_path()), exist_ok=True)
        open(status_last_path(), "w").write("{}")
        print(
command 151
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py::test_2750_report_that_failed_to_print_leaves_status_last_as_it_was

before 40
12c7e7930def08f9f0cb26d94579f6c7e23a0556
keep 67
skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py
command 336
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpclocydze/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py::test_2750_report_starts_no_refresh_when_the_snapshot_is_no_older_than_the_max_age

file 33
skills/tdd/scripts/veri/status.py
old 59
if age > int(tunables.read("VERI_SNAPSHOT_MAX_AGE", "60")):
new 8
if True:
command 166
make test TESTS=skills/tdd/scripts/tests/py/unit/test_status_report_last_written.py::test_2750_report_starts_no_refresh_when_the_snapshot_is_no_older_than_the_max_age

