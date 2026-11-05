file 39
skills/tdd/scripts/veri/tests_frozen.py
old 54
head_text = _text_at("HEAD", name, subprocess.DEVNULL)
new 52
head_text = _text_at(base, name, subprocess.DEVNULL)
command 207
make test TESTS=skills/tdd/scripts/tests/py/test_tests_frozen_process.py::test_rerecord_earlier_rewrites_body_and_helpers_lines_together_from_head_when_a_diff_checked_step_makes_a_case_call_a_new_helper_3052

