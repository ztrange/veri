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

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 92
next((c for c in fresh if _body_digest(at_head[c].replace(c, case)) == parsed[2]), fresh[0])
new 8
fresh[0]
command 329
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpo3p2a8j9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tick_ledger_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tick_ledger_process.py::test_ticking_pairs_each_work_tree_renamed_case_with_its_missing_title_by_body_not_by_position_2825

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 47
at_head, before = tree, _cases_at("HEAD", name)
new 14
at_head = tree
command 316
/private/var/folders/bm/b7qc5gy14kj4qmrgkj2zb5vw0000gp/T/tmpo3p2a8j9/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tick_ledger_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tick_ledger_process.py::test_ticking_does_not_pair_a_missing_title_with_a_case_already_committed_in_head_2825

