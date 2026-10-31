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

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 60
return _body_line(name, case, _cases_at("HEAD", name)[case])
new 13
return record
command 346
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwd8fn17e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_re_records_an_earlier_steps_case_whose_body_the_refactor_moved_into_a_shared_helper_2626

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 179
        head = _cases_at("HEAD", name)[case]
        if _assertion_lines(head) != _assertion_lines(verified):
            return record
        return _body_line(name, case, head)
new 246
        hc = _cases_at("HEAD", name)
        case = case if case in hc else list(hc)[1]
        head = hc[case]
        if _assertion_lines(head) != _assertion_lines(verified):
            return record
        return _body_line(name, case, head)
command 338
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwd8fn17e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_leaves_a_cases_record_when_the_refactor_changed_its_title_and_body_together_2626

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 32
if handle.read().strip() != "0":
new 9
if False:
command 171
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_re_records_nothing_and_exits_3_unless_verdict_refactor_exit_holds_0_2626

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 42
except FileNotFoundError:
        return 3
new 38
except FileNotFoundError:
        pass
command 171
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_refactored_re_records_nothing_and_exits_3_unless_verdict_refactor_exit_holds_0_2626

file 39
skills/tdd/scripts/veri/tests_frozen.py
old 45
if nows and _changed_by_refactor(name, case):
new 36
if _changed_by_refactor(name, case):
command 339
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpwd8fn17e/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_tests_frozen_process.py make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_check_earlier_names_a_case_deleted_from_the_tree_after_a_refactor_commit_as_removed_not_as_stale_2626

