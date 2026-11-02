file 39
skills/tdd/scripts/veri/tests_frozen.py
old 33
if case not in at_head and fresh:
new 23
if case not in at_head:
command 341
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpuok1kojk/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tick_ledger_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tick_ledger_process.py::test_ticking_refactor_pending_leaves_a_record_unwritten_when_a_recorded_case_is_missing_with_no_fresh_one_2825

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 58
return 0 if not changed or _write_record(path, out) else 2
new 43
return 0 if _write_record(path, out) else 2
command 341
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpuok1kojk/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tick_ledger_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tick_ledger_process.py::test_ticking_refactor_pending_leaves_a_record_unwritten_when_a_recorded_case_is_missing_with_no_fresh_one_2825

