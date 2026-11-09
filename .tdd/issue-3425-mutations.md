file 38
skills/tdd/scripts/veri/tick_ledger.py
old 23
"test", f"TESTS={case}"
new 25
"test", f"TESTS=x/{case}"
context 71
    return subprocess.run(["make", "test", f"TESTS={case}"]).returncode
command 173
make test TESTS=skills/tdd/scripts/tests/py/unit/test_tick_ledger_already_holds.py::test_run_case_in_a_repo_declaring_no_one_test_file_command_runs_make_test_tests_case_3425

