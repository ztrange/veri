file 38
skills/tdd/scripts/veri/rerun_alone.py
old 61
 or re.findall(r"^(?:FAILED|ERROR) (\S+?\.py)::", text, re.M)
new 0

command 174
make test TESTS=skills/tdd/scripts/tests/py/test_rerun_alone_process.py::test_pytest_failed_line_naming_a_unit_file_reruns_it_alone_once_and_writes_one_suite_flake_event_2933

before 40
2916e6d82470b2a4da4637a651d03e446d9d5e3f
keep 55
skills/tdd/scripts/tests/py/test_rerun_alone_process.py
command 399
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpbx4i_8ox/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_rerun_alone_process.py::test_bare_test_py_path_still_red_alone_exits_1_and_writes_no_suite_flake_event_2933 make test TESTS=skills/tdd/scripts/tests/py/test_rerun_alone_process.py::test_bare_test_py_path_still_red_alone_exits_1_and_writes_no_suite_flake_event_2933
green 40
4a3850788930d151519b375d0a6c19a8337df640

