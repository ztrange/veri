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

