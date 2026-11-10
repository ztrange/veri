before 40
0c22e1761008c4cc4a4d838f46b2a39f7d07da9e
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 206
make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3477_leaving_the_watch_logs_pid_file_unreadable_for_a_garbled_pid_file_and_pid_dead_when_the_recorded_pid_cannot_be_signalled

before 40
0c22e1761008c4cc4a4d838f46b2a39f7d07da9e
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 187
make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3477_after_a_not_live_read_then_a_live_read_leaving_the_watch_logs_only_the_final_three_consecutive_misses

before 40
0c22e1761008c4cc4a4d838f46b2a39f7d07da9e
keep 58
skills/tdd/scripts/tests/py/unit/test_restart_conductor.py
command 200
make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3477_a_conductor_reading_not_live_for_three_polls_because_its_own_command_lacks_claude_is_watched_until_the_pid_is_dead

file 44
skills/tdd/scripts/veri/restart_conductor.py
old 68
if misses >= 3 and reasons[-1] in ("parent command", "own command"):
new 15
if misses >= 3:
context 84
                if misses >= 3 and reasons[-1] in ("parent command", "own command"):
command 184
make test TESTS=skills/tdd/scripts/tests/py/unit/test_restart_conductor.py::test_3477_a_conductor_whose_recorded_pid_is_dead_for_three_polls_ends_the_watch_with_restarts_7_0_and_exit_0

