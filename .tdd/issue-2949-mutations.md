file 41
skills/tdd/scripts/veri/red_divergence.py
old 49
tuple(fields.get(key, "") for key in REASON_KEYS)
new 87
tuple(fields.get(key, "") if key == "PREDICTED_FAILURE" else "" for key in REASON_KEYS)
command 198
make test TESTS=skills/tdd/scripts/tests/py/unit/test_red_divergence.py::test_main_2949_writes_a_reason_holding_both_the_fail_output_and_the_prediction_note_of_a_red_revise_report_that_says_diverged

before 40
9a50dd4f6ff455bd36c5876c5af510d03384cb4c
keep 61
skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py
command 374
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp0h5b0h6d/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py::test_main_renders_a_red_revise_prompt_asking_for_fail_output_and_prediction_note_and_naming_both_in_its_report_format_key_list_2949

