before 40
6bacf6d121fbe48115c58f7429c27ab60200c482
keep 63
skills/tdd/scripts/tests/py/unit/test_clear_refactor_pending.py
command 366
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpdw61edbn/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_clear_refactor_pending.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_clear_refactor_pending.py::test_main_clears_the_mark_exiting_0_and_leaves_every_other_ledger_line_unchanged_when_the_receipts_sha_equals_head_2972

file 49
skills/tdd/scripts/veri/clear_refactor_pending.py
old 46
    left = ledger.rewrite_ledger(argv[0], new)
new 59
    return 3
    left = ledger.rewrite_ledger(argv[0], new)
command 200
make test TESTS=skills/tdd/scripts/tests/py/unit/test_clear_refactor_pending.py::test_main_clears_the_mark_exiting_0_and_leaves_every_other_ledger_line_unchanged_when_the_receipts_sha_equals_head_2972

file 38
skills/tdd/scripts/veri/tick_ledger.py
old 43
if tests_frozen.is_diff_checked(step_line):
new 8
if True:
command 193
make test TESTS=skills/tdd/scripts/tests/py/unit/test_tick_ledger.py::test_main_ticks_a_step_not_marked_diff_checked_with_no_pin_recheck_receipt_for_a_plain_refactor_pending_and_phase_tick_2972

