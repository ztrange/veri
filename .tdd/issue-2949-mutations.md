file 41
skills/tdd/scripts/veri/red_divergence.py
old 49
tuple(fields.get(key, "") for key in REASON_KEYS)
new 87
tuple(fields.get(key, "") if key == "PREDICTED_FAILURE" else "" for key in REASON_KEYS)
command 198
make test TESTS=skills/tdd/scripts/tests/py/unit/test_red_divergence.py::test_main_2949_writes_a_reason_holding_both_the_fail_output_and_the_prediction_note_of_a_red_revise_report_that_says_diverged

