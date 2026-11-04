file 38
skills/tdd/scripts/veri/rerun_alone.py
old 61
 or re.findall(r"^(?:FAILED|ERROR) (\S+?\.py)::", text, re.M)
new 0

command 174
make test TESTS=skills/tdd/scripts/tests/py/test_rerun_alone_process.py::test_pytest_failed_line_naming_a_unit_file_reruns_it_alone_once_and_writes_one_suite_flake_event_2933

