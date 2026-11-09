before 40
c213ba12d93457510c7e4bcb1cab68479b11fa63
keep 60
skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py
command 200
make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py::test_main_lists_only_this_issues_named_author_less_units_sorted_past_an_unreadable_log_line_and_only_in_a_diff_prompt_3404

file 46
skills/tdd/scripts/veri/build_verify_prompt.py
old 36
and str(e.get("issue")) == issue and
new 3
and
command 187
make test TESTS=skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py::test_main_renders_a_diff_prompt_without_the_author_less_block_when_the_log_holds_no_event_for_this_issue_3404

