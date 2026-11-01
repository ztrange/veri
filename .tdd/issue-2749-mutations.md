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

