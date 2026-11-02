file 32
skills/tdd/scripts/veri/event.py
old 34
if not (owner and repo and issue):
new 24
if not (owner and repo):
command 325
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_journal_defaults_to_dot_veri_and_skips_a_clone_without_origin_url_or_an_event_without_issue

file 32
skills/tdd/scripts/veri/event.py
old 34
if not (owner and repo and issue):
new 15
if not (issue):
command 325
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_journal_defaults_to_dot_veri_and_skips_a_clone_without_origin_url_or_an_event_without_issue

file 32
skills/tdd/scripts/veri/event.py
old 9
"~/.veri"
new 7
"~/.vx"
command 325
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_journal_defaults_to_dot_veri_and_skips_a_clone_without_origin_url_or_an_event_without_issue

file 32
skills/tdd/scripts/veri/event.py
old 42
if text.startswith("url") and "=" in text:
new 26
if text.startswith("url"):
command 326
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_clone_without_readable_git_config_writes_no_journal_and_a_url_word_without_equals_is_skipped

file 32
skills/tdd/scripts/veri/event.py
old 35
except OSError:
        return None
new 45
except ZeroDivisionError:
        return None
command 326
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_clone_without_readable_git_config_writes_no_journal_and_a_url_word_without_equals_is_skipped

file 32
skills/tdd/scripts/veri/event.py
old 34
if not (owner and repo and issue):
new 24
if not (owner and repo):
command 320
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_event_with_an_empty_issue_creates_nothing_under_veri_home_and_prints_nothing_on_stderr

file 32
skills/tdd/scripts/veri/event.py
old 34
if not (owner and repo and issue):
new 13
if not issue:
command 333
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_event_in_a_clone_with_no_origin_remote_creates_nothing_under_veri_home_and_prints_nothing_on_stderr

file 32
skills/tdd/scripts/veri/event.py
old 29
os.path.expanduser("~/.veri")
new 30
os.path.expanduser("~/.veriX")
command 300
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_with_veri_home_unset_the_journal_is_written_under_dot_veri_in_home

file 32
skills/tdd/scripts/veri/event.py
old 82
os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
    try:
        os.write(fd, data)
new 68
os.O_WRONLY | os.O_CREAT, 0o666)
    try:
        os.write(fd, data)
command 315
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_one_journal_write_starts_no_process_and_is_one_os_write_on_an_o_append_descriptor

file 32
skills/tdd/scripts/veri/event.py
old 26
        os.write(fd, data)
new 54
        os.write(fd, data[:1]); os.write(fd, data[1:])
command 315
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_one_journal_write_starts_no_process_and_is_one_os_write_on_an_o_append_descriptor

file 39
skills/tdd/scripts/tests/py/conftest.py
old 46
monkeypatch.setenv("VERI_HOME", str(tmp_path))
new 46
monkeypatch.delenv("VERI_HOME", raising=False)
command 317
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_event.py make test TESTS=skills/tdd/scripts/tests/py/test_event.py::test_event_sh_under_hermetic_environment_writes_its_journal_under_tmp_path_and_leaves_the_real_veri_home_untouched

file 57
skills/tdd/scripts/tests/py/test_run_conductor_process.py
old 31
 .tdd/wt/2627/.tdd/events.jsonl
new 0

command 188
make test TESTS=skills/tdd/scripts/tests/py/test_run_conductor_process.py::test_main_leaves_a_runnable_pinned_script_under_a_worktree_cut_during_the_run_when_the_conductor_bails_issue_2627

file 42
skills/tdd/scripts/veri/add_ledger_step.py
old 38
os.path.dirname(os.path.abspath(path))
new 21
os.path.dirname(path)
command 339
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpqnjolu2e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_add_ledger_step.py::test_2749_a_growing_call_given_a_relative_ledger_path_writes_the_plan_event_to_the_ledgers_own_events_file

file 40
skills/tdd/scripts/veri/run_conductor.py
old 24
"conductor-start", ["pid
new 25
"conductor-startx", ["pid
command 328
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_parallel_conductors.py make test TESTS=skills/tdd/scripts/tests/py/test_parallel_conductors.py::test_an_in_place_launch_leaves_the_conductors_event_log_holding_done_for_the_issue_it_solved_2814

file 32
skills/tdd/scripts/veri/event.py
old 59
clocked = all("awake" in m for m in marks if "ts" in m) and
new 18
clocked = True and
command 343
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_without_a_resume_skips_unparseable_lines_and_leaves_out_awake_seconds_when_a_mark_lacks_an_awake_reading

file 32
skills/tdd/scripts/veri/event.py
old 26
if isinstance(mark, dict):
new 8
if True:
command 343
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_without_a_resume_skips_unparseable_lines_and_leaves_out_awake_seconds_when_a_mark_lacks_an_awake_reading

file 32
skills/tdd/scripts/veri/event.py
old 28
if "ts" in opening else None
new 17
if True else None
command 344
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_figures_for_a_ts_less_mark_an_opening_without_ts_or_awake_an_unreadable_ending_and_a_missing_or_empty_log

file 32
skills/tdd/scripts/veri/event.py
old 47
if clocked and opening.get("awake") is not None
new 10
if clocked
command 344
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_figures_for_a_ts_less_mark_an_opening_without_ts_or_awake_an_unreadable_ending_and_a_missing_or_empty_log

file 32
skills/tdd/scripts/veri/event.py
old 29
marks[0] if marks else ending
new 6
ending
command 344
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_figures_for_a_ts_less_mark_an_opening_without_ts_or_awake_an_unreadable_ending_and_a_missing_or_empty_log

file 32
skills/tdd/scripts/veri/event.py
old 24
decode(errors="replace")
new 8
decode()
command 319
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_still_records_wall_and_awake_seconds_when_the_log_holds_a_line_of_non_utf8_bytes

file 32
skills/tdd/scripts/veri/event.py
old 78
tunables.read("VERI_LABEL", "ready-for-agent", unless_empty="ready-for-agent")
new 46
tunables.read("VERI_LABEL", "ready-for-agent")
command 309
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_done_records_lane_ready_for_agent_when_veri_label_is_set_to_an_empty_string

file 32
skills/tdd/scripts/veri/event.py
old 70
    home = tunables.read("VERI_HOME") or os.path.expanduser("~/.veri")
new 90
    home = tunables.read("VERI_HOME") or os.path.expanduser("~/.veri")
    os.remove(home)
command 321
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_nothing_in_skills_outside_the_tests_deletes_from_veri_home_or_copies_a_transcript_there

file 33
skills/tdd/scripts/veri/status.py
old 6
import
new 18
# VERI_HOME
import
command 310
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpiobhr7i9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_event_journal.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_event_journal.py::test_only_event_py_outside_the_tests_names_veri_home_so_nothing_else_writes_there

