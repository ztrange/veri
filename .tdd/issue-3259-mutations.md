before 40
dc89bd7cf63b6d9dfacca23148cfeee9a97c38e9
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 160
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_stopped_exits_2_naming_the_missing_stop_event_and_posts_nothing_when_the_journal_has_none

file 34
skills/tdd/scripts/veri/comment.py
old 20
    if stop is None:
new 13
    if False:
context 20
    if stop is None:
command 160
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_stopped_exits_2_naming_the_missing_stop_event_and_posts_nothing_when_the_journal_has_none

before 40
dc89bd7cf63b6d9dfacca23148cfeee9a97c38e9
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 172
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_stopped_posts_the_operator_stop_comment_with_the_resume_command_when_restart_pending_names_a_dead_pid

before 40
dc89bd7cf63b6d9dfacca23148cfeee9a97c38e9
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 180
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_stopped_posts_the_operator_stop_comment_with_the_resume_command_when_restart_pending_holds_garbage_or_nothing

file 34
skills/tdd/scripts/veri/comment.py
old 54
    except (OSError, ValueError):
        return False
new 83
    except OSError:
        return False
    except ValueError:
        return True
context 33
    except (OSError, ValueError):
command 180
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_stopped_posts_the_operator_stop_comment_with_the_resume_command_when_restart_pending_holds_garbage_or_nothing

before 40
dc89bd7cf63b6d9dfacca23148cfeee9a97c38e9
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 172
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_stopped_posts_the_operator_stop_comment_with_the_resume_command_when_restart_pending_names_a_dead_pid

before 40
dc89bd7cf63b6d9dfacca23148cfeee9a97c38e9
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 252
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_every_heading_comment_sh_posts_for_bailed_and_stopped_is_classified_by_comment_class_as_the_hand_composed_heading_is_and_falls_in_its_metrics_family_and_the_bailed_one_reads_as_bail

