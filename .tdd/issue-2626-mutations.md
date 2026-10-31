file 39
skills/tdd/scripts/veri/tests_frozen.py
old 117
        lines = handle.read().splitlines()
    os.chdir(_toplevel())

    def rewrite(_, record, name, case, digest):
new 124
        lines = handle.read().splitlines()
    os.chdir(_toplevel() or ".")

    def rewrite(_, record, name, case, digest):
command 324
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwd8fn17e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_run_outside_any_git_repository_exits_2_and_re_records_nothing_2626

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 208
    with open(ledger, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    os.chdir(_toplevel())

    def rewrite(_, record, name, case, digest):
        if _body_digest(_cases_at(green
new 262
    try:
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return 0
    os.chdir(_toplevel())

    def rewrite(_, record, name, case, digest):
        if _body_digest(_cases_at(green
command 311
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwd8fn17e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_unreadable_ledger_exits_2_and_re_records_nothing_2626

