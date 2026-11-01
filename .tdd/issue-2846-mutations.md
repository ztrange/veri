file 40
skills/tdd/scripts/veri/parse_verdict.py
old 52
        elif in_block:
            kept.append(line)
new 49
        elif False:
            kept.append(line)
command 348
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp0yygeh2c/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_parse_verdict.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_parse_verdict.py::test_issue_2846_a_missing_test_line_before_a_multiline_reason_and_reject_verdict_is_printed_intact_then_the_whole_block

file 40
skills/tdd/scripts/veri/parse_verdict.py
old 29
    if after:
        missing
new 29
    if False:
        missing
command 342
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp0yygeh2c/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_parse_verdict.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_parse_verdict.py::test_issue_2846_a_multiline_reason_before_the_reject_verdict_with_reason_text_after_it_prints_only_the_text_after

