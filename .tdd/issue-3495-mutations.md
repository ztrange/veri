before 40
5690fdb3cecb1a6cff65340d112c43f76ce52d89
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 184
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_nothing_on_the_tick_where_a_run_seen_live_is_restarting_beside_one_live_run_at_target_2_issue_3495

before 40
e4908614f1eaae4078bcb1a64795fd7b1656619b
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 205
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_exactly_one_at_target_4_once_a_restarted_run_is_live_again_beside_a_live_run_and_a_never_seen_restarting_run_issue_3495

file 35
skills/tdd/scripts/veri/dispatch.py
old 79
    except ProcessLookupError:
        return False
    except PermissionError:
new 78
    except ProcessLookupError:
        return True
    except PermissionError:
context 30
    except ProcessLookupError:
command 202
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_the_next_issue_at_target_2_beside_one_live_run_and_a_worktree_whose_restart_marker_names_a_dead_restarter_issue_3495

before 40
0c22e1761008c4cc4a4d838f46b2a39f7d07da9e
keep 49
skills/tdd/scripts/tests/py/unit/test_dispatch.py
command 184
make test TESTS=skills/tdd/scripts/tests/py/unit/test_dispatch.py::test_main_launches_nothing_on_the_tick_where_a_run_seen_live_is_restarting_beside_one_live_run_at_target_2_issue_3495

