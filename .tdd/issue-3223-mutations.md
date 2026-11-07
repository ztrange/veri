before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 47
skills/tdd/scripts/tests/py/unit/test_growth.py
command 313
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_growth.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_growth.py::test_growth_skips_records_with_no_usage_so_a_later_one_leaves_the_context_at_the_last_usage_record

file 33
skills/tdd/scripts/veri/growth.py
old 64
usage = record.get("message", {}).get("usage")
        if usage:
new 151
usage = record.get("message", {}).get("usage") or {"input_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
        if usage:
command 163
make test TESTS=skills/tdd/scripts/tests/py/unit/test_growth.py::test_growth_skips_records_with_no_usage_so_a_later_one_leaves_the_context_at_the_last_usage_record

before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 47
skills/tdd/scripts/tests/py/unit/test_growth.py
command 298
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_growth.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_growth.py::test_growth_reads_a_session_transcript_row_without_type_assistant_as_a_usage_record

file 33
skills/tdd/scripts/veri/growth.py
old 9
if usage:
new 47
if usage and record.get("type") == "assistant":
command 148
make test TESTS=skills/tdd/scripts/tests/py/unit/test_growth.py::test_growth_reads_a_session_transcript_row_without_type_assistant_as_a_usage_record

before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 342
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_restart_conductor.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3223_while_the_conductor_is_alive_the_watch_waits_through_the_sleep_wrapper_with_a_positive_interval

before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 307
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_restart_conductor.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3223_the_sleep_wrapper_waits_by_handing_the_seconds_to_time_sleep

before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 322
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_restart_conductor.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3223_a_live_conductor_whose_growth_is_59499_with_the_default_knob_is_not_stopped

before 40
58855a40b58832d399de0a90ccf1ee2038ed676d
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 353
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpukohdusu/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_restart_conductor.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3223_the_stop_wrapper_started_from_a_linked_worktree_writes_the_at_ledger_stop_file_under_the_main_working_tree

